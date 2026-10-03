"""
Generator for 200 synthetic Portuguese commercial lease PDFs.
Produces a ground_truth.csv alongside the PDFs for LangSmith evaluation.

Distribution:
  30  standard office leases
  25  standard retail leases
  20  standard warehouse/industrial leases
  25  leases with break option conditions
  20  leases with unusual rent review
  20  leases with assignment restrictions
  15  leases with missing mandatory fields
  15  short-term leases (under 1 year)
  15  high-risk combinations
  15  Portugal compliance issues
  ─── 200 total

Each lease is unique: randomised parties, NIF, address, rent, dates, clauses.
Ground truth is deterministic so results can be scored automatically.
"""

import csv
import random
import string
from pathlib import Path
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# ── output dirs ───────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("data/leases/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── seed for reproducibility ──────────────────────────────────────────────────
random.seed(42)

# ── data pools ────────────────────────────────────────────────────────────────
TENANT_COMPANIES = [
    "Tecnidata Sistemas Lda.", "Grupo Meridiano S.A.", "Atlântico Retail Unipessoal Lda.",
    "Iberostar Logistics Lda.", "NovaBuild Construções S.A.", "SolTejo Energia Lda.",
    "Lusitana Pharma S.A.", "Porto Digital Solutions Lda.", "Algarve Hospitality Group S.A.",
    "Tagus Trading Lda.", "EurobuildPT S.A.", "Setúbal Warehousing Lda.",
    "Braga Tech Hub Lda.", "Cascais Retail Partners S.A.", "Faro Logistics Unipessoal Lda.",
    "Sintra Innovation Lda.", "Coimbra Medical Supplies S.A.", "Évora Agricultural Tech Lda.",
    "Viseu Industrial Group S.A.", "Funchal Tourism Services Lda.", "Aveiro Marine Lda.",
    "Leiria Construction S.A.", "Santarém Food Processing Lda.", "Almada Retail S.A.",
    "Barreiro Industrial Lda.", "Montijo Logistics Park S.A.", "Odivelas Commerce Lda.",
    "Loures Business Center S.A.", "Amadora Tech Solutions Lda.", "Vila Franca Commerce Lda.",
    "Queluz Retail Group S.A.", "Caldas da Rainha Industrial Lda.", "Peniche Maritime S.A.",
    "Nazaré Tourism Lda.", "Óbidos Heritage Commerce S.A.", "Torres Vedras Agro S.A.",
    "Palmela Auto Components Lda.", "Alcochete Distribution Lda.", "Seixal Steel Works S.A.",
    "Moita Port Services Lda.",
]

LANDLORD_COMPANIES = [
    "Fundo de Investimento Imobiliário Tejo SICAV-FIA",
    "Lisboa Property Fund S.A.",
    "Iberian Real Estate Partners Lda.",
    "Douro Capital Properties S.A.",
    "Atlantic Estates Portugal Lda.",
    "Peninsular Property Trust SICAV",
    "Tagus Commercial Properties S.A.",
    "Algarve Investment Fund SICAV-FIA",
    "Porto Heritage Properties Lda.",
    "Lusitania Commercial Estates S.A.",
    "Minho Valley Properties Lda.",
    "Alentejo Land Fund SICAV-FIA",
    "Costa Verde Real Estate S.A.",
    "Serra da Arrábida Properties Lda.",
    "Montado Capital Fund SICAV",
]

STREETS = [
    "Avenida da Liberdade", "Rua Augusta", "Avenida Almirante Reis",
    "Rua de São Bento", "Avenida da República", "Rua do Ouro",
    "Avenida Fontes Pereira de Melo", "Rua Garrett", "Praça do Comércio",
    "Avenida 24 de Julho", "Rua dos Correeiros", "Avenida João XXI",
    "Rua Castilho", "Avenida Duque de Loulé", "Rua Braamcamp",
    "Avenida Eng. Duarte Pacheco", "Rua Latino Coelho", "Avenida de Berna",
    "Rua Joaquim António de Aguiar", "Avenida Defensores de Chaves",
]

CITIES = [
    ("Lisboa", "1000"), ("Lisboa", "1100"), ("Lisboa", "1200"),
    ("Lisboa", "1300"), ("Lisboa", "1400"), ("Lisboa", "1500"),
    ("Porto", "4000"), ("Porto", "4100"), ("Porto", "4200"),
    ("Braga", "4700"), ("Coimbra", "3000"), ("Setúbal", "2900"),
    ("Faro", "8000"), ("Évora", "7000"), ("Aveiro", "3800"),
    ("Viseu", "3500"), ("Leiria", "2400"), ("Santarém", "2000"),
    ("Castelo Branco", "6000"), ("Guarda", "6300"),
]

DISTRICTS = {
    "Lisboa": "Lisboa", "Porto": "Porto", "Braga": "Braga",
    "Coimbra": "Centro", "Setúbal": "Setúbal", "Faro": "Algarve",
    "Évora": "Alentejo", "Aveiro": "Centro", "Viseu": "Centro",
    "Leiria": "Centro", "Santarém": "Ribatejo", "Castelo Branco": "Interior",
    "Guarda": "Interior",
}

PROPERTY_TYPES = {
    "office": ["escritórios", "espaço de escritório", "centro de negócios"],
    "retail": ["loja", "espaço comercial", "estabelecimento comercial"],
    "warehouse": ["armazém", "espaço industrial", "unidade logística"],
}

PERMITTED_USES = {
    "office": "uso exclusivo de escritório e atividades administrativas",
    "retail": "comércio a retalho e atividades comerciais conexas",
    "warehouse": "armazenagem, logística e operações industriais",
}


# ── helpers ───────────────────────────────────────────────────────────────────
def random_nif() -> str:
    """Generate a plausible Portuguese NIF (9 digits starting with 5 for companies)."""
    return "5" + "".join([str(random.randint(0, 9)) for _ in range(8)])


def random_date(start_year=2020, end_year=2025) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_rent(prop_type: str) -> tuple:
    """Return (monthly_rent, annual_rent) in EUR."""
    ranges = {
        "office": (2000, 25000),
        "retail": (800, 15000),
        "warehouse": (1500, 20000),
    }
    lo, hi = ranges[prop_type]
    monthly = random.randrange(lo, hi, 100)
    return monthly, monthly * 12


def random_sqm(prop_type: str) -> int:
    ranges = {
        "office": (100, 3000),
        "retail": (50, 800),
        "warehouse": (500, 10000),
    }
    lo, hi = ranges[prop_type]
    return random.randrange(lo, hi, 50)


def random_address() -> tuple:
    street = random.choice(STREETS)
    number = random.randint(1, 300)
    city, postcode = random.choice(CITIES)
    full_postcode = f"{postcode}-{random.randint(100, 999):03d}"
    return f"{street} {number}", city, full_postcode


def make_pdf(filepath: Path, content: list):
    """Render content list to a PDF file."""
    doc = SimpleDocTemplate(
        str(filepath), pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'T', parent=styles['Heading1'],
        alignment=TA_CENTER, fontSize=12, spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=10, spaceAfter=5, spaceBefore=10
    )
    body_style = ParagraphStyle(
        'B', parent=styles['Normal'],
        fontSize=9, leading=13, alignment=TA_JUSTIFY, spaceAfter=5
    )
    story = []
    for line in content:
        if line.startswith("##"):
            story.append(Paragraph(line[2:].strip(), h2_style))
        elif line.startswith("#"):
            story.append(Paragraph(line[1:].strip(), title_style))
        elif line == "---":
            story.append(Spacer(1, 0.25*cm))
        else:
            story.append(Paragraph(line, body_style))
    doc.build(story)


# ── lease builders ────────────────────────────────────────────────────────────

def build_standard_lease(prop_type: str, category: str, idx: int) -> dict:
    """Build a clean standard lease with all mandatory fields present."""
    tenant = random.choice(TENANT_COMPANIES)
    landlord = random.choice(LANDLORD_COMPANIES)
    nif_t = random_nif()
    nif_l = random_nif()
    street, city, postcode = random_address()
    sqm = random_sqm(prop_type)
    monthly_rent, annual_rent = random_rent(prop_type)
    start_date = random_date(2021, 2024)
    duration_years = random.choice([3, 5, 7, 10])
    end_date = date(start_date.year + duration_years, start_date.month, start_date.day)
    deposit_months = random.choice([2, 3])
    deposit = monthly_rent * deposit_months
    prop_desc = random.choice(PROPERTY_TYPES[prop_type])
    permitted_use = PERMITTED_USES[prop_type]
    notice_tenant = 120 if duration_years >= 1 else 60
    notice_landlord = 240 if duration_years >= 6 else 120

    # break option at midpoint
    break_year = start_date.year + duration_years // 2
    break_date = date(break_year, start_date.month, start_date.day)
    break_penalty = monthly_rent * 3

    content = [
        f"# CONTRATO DE ARRENDAMENTO COMERCIAL",
        f"# Referência: PT-{idx:04d}-{prop_type.upper()[:3]}",
        "---",
        f"O presente Contrato de Arrendamento Comercial (\"Contrato\") é celebrado em "
        f"{start_date.strftime('%d de %B de %Y')}, entre:",
        f"<b>SENHORIO:</b> {landlord}, com sede em Lisboa, Portugal, com o número de "
        f"identificação fiscal (NIF) {nif_l} (\"Senhorio\");",
        f"<b>ARRENDATÁRIO:</b> {tenant}, com sede em {city}, Portugal, com o número de "
        f"identificação fiscal (NIF) {nif_t} (\"Arrendatário\").",
        "## 1. OBJECTO DO CONTRATO",
        f"O Senhorio arrenda ao Arrendatário o {prop_desc} sito em {street}, "
        f"{postcode} {city}, Portugal, com uma área aproximada de {sqm} metros quadrados "
        f"(\"Imóvel\").",
        "## 2. PRAZO",
        f"O prazo do arrendamento inicia-se em {start_date.isoformat()} "
        f"(\"Data de Início\") e termina em {end_date.isoformat()} "
        f"(\"Data de Fim\"), pelo período de {duration_years} anos, renovando-se "
        f"automaticamente por períodos iguais salvo oposição das partes.",
        "## 3. OPÇÃO DE RESOLUÇÃO ANTECIPADA",
        f"O Arrendatário tem o direito de resolver o presente Contrato em "
        f"{break_date.isoformat()} (\"Data de Resolução\"), mediante: (a) aviso prévio "
        f"escrito com antecedência mínima de 120 (cento e vinte) dias; (b) ausência de "
        f"incumprimento material na Data de Resolução; (c) pagamento de uma indemnização "
        f"equivalente a {deposit_months + 1} meses de renda no valor de "
        f"EUR {break_penalty:,.0f}.",
        "## 4. RENDA",
        f"A renda mensal é de EUR {monthly_rent:,.0f} ({"" + str(monthly_rent) + ""} euros), "
        f"pagável no primeiro dia de cada mês. A renda anual total é de "
        f"EUR {annual_rent:,.0f}.",
        "## 5. ACTUALIZAÇÃO DE RENDA",
        f"A renda será actualizada anualmente de acordo com o Índice de Preços no "
        f"Consumidor (IPC) publicado pelo Instituto Nacional de Estatística (INE). "
        f"O Senhorio notificará o Arrendatário com antecedência mínima de 30 dias.",
        "## 6. DEPÓSITO DE GARANTIA",
        f"O Arrendatário entrega ao Senhorio um depósito de garantia de "
        f"EUR {deposit:,.0f} (equivalente a {deposit_months} meses de renda), "
        f"devolvido no prazo de 30 dias após o termo do Contrato, deduzido de eventuais "
        f"valores em dívida.",
        "## 7. USO PERMITIDO",
        f"O Imóvel destina-se exclusivamente a {permitted_use}. Qualquer alteração "
        f"de uso requer autorização escrita prévia do Senhorio.",
        "## 8. CESSÃO E SUBARRENDAMENTO",
        f"O Arrendatário não pode ceder, subarrendar ou transmitir os seus direitos "
        f"ao abrigo do presente Contrato sem consentimento prévio e escrito do Senhorio, "
        f"o qual não será recusado sem motivo justificado.",
        "## 9. ENCARGOS DE CONDOMÍNIO",
        f"O Arrendatário suporta os encargos de condomínio e demais despesas correntes "
        f"do Imóvel, estimados em EUR {monthly_rent * 0.08:,.0f} mensais, sujeitos a "
        f"actualização anual.",
        "## 10. REGISTO DO CONTRATO",
        f"O Senhorio obriga-se a comunicar o presente Contrato ao Portal das Finanças "
        f"(Autoridade Tributária — AT) até ao final do mês seguinte ao início do "
        f"arrendamento, nos termos do NRAU (Lei n.º 6/2006, de 27 de Fevereiro).",
        "## 11. IMPOSTO DO SELO",
        f"O Imposto do Selo, correspondente a 10% de uma mensalidade de renda "
        f"(EUR {monthly_rent * 0.10:,.0f}), é da responsabilidade do Senhorio, "
        f"nos termos da legislação fiscal portuguesa em vigor.",
        "## 12. PRAZOS DE AVISO PRÉVIO",
        f"Para efeitos de resolução ou oposição à renovação: (a) o Arrendatário deve "
        f"notificar o Senhorio com antecedência de {notice_tenant} dias; (b) o Senhorio "
        f"deve notificar o Arrendatário com antecedência de {notice_landlord} dias.",
        "## 13. OBRAS E BENFEITORIAS",
        f"O Arrendatário não pode realizar obras ou alterações no Imóvel sem prévia "
        f"autorização escrita do Senhorio. As benfeitorias realizadas revertem para o "
        f"Senhorio no termo do Contrato, salvo acordo em contrário.",
        "## 14. OBRIGAÇÕES DO ARRENDATÁRIO",
        f"O Arrendatário obriga-se a: (a) pagar a renda na data acordada; "
        f"(b) conservar o Imóvel em bom estado; (c) cumprir toda a legislação aplicável; "
        f"(d) manter seguro de responsabilidade civil de valor não inferior a "
        f"EUR {max(1000000, annual_rent * 5):,.0f}.",
        "## 15. OBRIGAÇÕES DO SENHORIO",
        f"O Senhorio obriga-se a: (a) manter a estrutura do edifício em bom estado; "
        f"(b) assegurar o gozo pacífico do Imóvel; (c) realizar obras estruturais "
        f"necessárias.",
        "## 16. LEI APLICÁVEL",
        f"O presente Contrato é regulado pela lei portuguesa, designadamente pelo "
        f"Novo Regime do Arrendamento Urbano (NRAU — Lei n.º 6/2006) e pelo Código Civil "
        f"Português. Qualquer litígio será submetido aos tribunais de {city}.",
        "---",
        f"Assinado em {city}, em {start_date.strftime('%d de %B de %Y')}.",
        f"{landlord} _________________________ Data: {start_date.isoformat()}",
        f"{tenant} _________________________ Data: {start_date.isoformat()}",
    ]

    ground_truth = {
        "filename": f"PT_{idx:04d}_{prop_type}_{city.replace(' ', '_')}.pdf",
        "category": category,
        "property_type": prop_type,
        "tenant_name": tenant,
        "landlord_name": landlord,
        "nif_tenant": nif_t,
        "nif_landlord": nif_l,
        "property_address": f"{street}, {postcode} {city}, Portugal",
        "lease_commencement_date": start_date.isoformat(),
        "lease_expiry_date": end_date.isoformat(),
        "rent_amount": f"EUR {monthly_rent:,.0f} per month / EUR {annual_rent:,.0f} per year",
        "break_option_date": break_date.isoformat(),
        "break_penalty_months": deposit_months + 1,
        "rent_review_mechanism": "CPI/INE annual",
        "security_deposit_months": deposit_months,
        "permitted_use": permitted_use,
        "financas_registration": "yes",
        "stamp_duty_party": "landlord",
        "notice_period_tenant_days": notice_tenant,
        "notice_period_landlord_days": notice_landlord,
        "governing_law": "Portuguese law / NRAU",
        "expected_flags": "none",
        "expected_risk_level": "low",
        "has_nif_tenant": "yes",
        "has_nif_landlord": "yes",
        "has_financas_clause": "yes",
        "assignment_absolute_prohibition": "no",
        "upward_only_review": "no",
        "stamp_duty_on_tenant": "no",
        "notice_below_statutory": "no",
        "deposit_above_6_months": "no",
    }

    return content, ground_truth


def build_break_option_lease(idx: int) -> dict:
    """Lease with problematic break option conditions."""
    base_content, gt = build_standard_lease("office", "break_option", idx)
    city = gt["property_address"].split(",")[-2].strip().split(" ")[-1]

    # replace break option clause with problematic version
    for i, line in enumerate(base_content):
        if "OPÇÃO DE RESOLUÇÃO ANTECIPADA" in line:
            # find the content after this heading
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("O Arrendatário"):
                    base_content[j] = (
                        "O Arrendatário tem o direito de resolver o presente Contrato "
                        "em " + gt["break_option_date"] + ", mediante: (a) aviso prévio "
                        "escrito com antecedência mínima de 120 dias; (b) ausência de "
                        "qualquer incumprimento, incluindo obrigações de conservação; "
                        "(c) pagamento de indemnização equivalente a 6 meses de renda; "
                        "e (d) <b>a responsabilidade por obras de conservação e "
                        "reposição do estado original não fica extinta com o exercício "
                        "da opção de resolução antecipada, mantendo-se o Senhorio com "
                        "o direito de reclamar os custos de obras necessárias após a "
                        "saída do Arrendatário.</b>"
                    )
                    break
            break

    gt["category"] = "break_option_issue"
    gt["expected_flags"] = "dilapidations_survival_on_break"
    gt["expected_risk_level"] = "high"
    return base_content, gt


def build_rent_review_lease(idx: int) -> dict:
    """Lease with unusual rent review (upward-only, waiver of downward)."""
    base_content, gt = build_standard_lease(
        random.choice(["office", "retail"]), "unusual_rent_review", idx
    )
    for i, line in enumerate(base_content):
        if "ACTUALIZAÇÃO DE RENDA" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("A renda"):
                    base_content[j] = (
                        "A renda será revista em cada aniversário do Contrato para o "
                        "valor de mercado determinado por perito independente. "
                        "<b>A revisão é exclusivamente ascendente, sendo expressamente "
                        "excluída qualquer redução da renda em resultado da revisão. "
                        "O Arrendatário renuncia expressamente ao direito de requerer "
                        "a redução da renda em qualquer circunstância.</b>"
                    )
                    break
            break
    gt["category"] = "unusual_rent_review"
    gt["rent_review_mechanism"] = "open market upward-only — downward waiver"
    gt["expected_flags"] = "upward_only_rent_review_waiver"
    gt["expected_risk_level"] = "medium"
    gt["upward_only_review"] = "yes"
    return base_content, gt


def build_assignment_restriction_lease(idx: int) -> dict:
    """Lease with absolute assignment prohibition."""
    base_content, gt = build_standard_lease(
        random.choice(["office", "retail", "warehouse"]),
        "assignment_restriction", idx
    )
    for i, line in enumerate(base_content):
        if "CESSÃO E SUBARRENDAMENTO" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("O Arrendatário"):
                    base_content[j] = (
                        "<b>O Arrendatário fica expressamente proibido de ceder, "
                        "subarrendar, transmitir ou de qualquer forma onerar os seus "
                        "direitos ao abrigo do presente Contrato, em quaisquer "
                        "circunstâncias e sem excepção. Esta proibição é absoluta e "
                        "não pode ser afastada por qualquer acordo posterior entre "
                        "as partes, incluindo no caso de transmissão do "
                        "estabelecimento comercial.</b>"
                    )
                    break
            break
    gt["category"] = "assignment_restriction"
    gt["assignment_absolute_prohibition"] = "yes"
    gt["expected_flags"] = "absolute_assignment_prohibition"
    gt["expected_risk_level"] = "high"
    return base_content, gt


def build_missing_fields_lease(idx: int) -> dict:
    """Lease missing mandatory Portuguese fields (NIF, Finanças, governing law)."""
    prop_type = random.choice(["office", "retail"])
    tenant = random.choice(TENANT_COMPANIES)
    landlord = random.choice(LANDLORD_COMPANIES)
    street, city, postcode = random_address()
    sqm = random_sqm(prop_type)
    monthly_rent, annual_rent = random_rent(prop_type)
    start_date = random_date(2021, 2024)
    duration_years = random.choice([3, 5])
    end_date = date(start_date.year + duration_years, start_date.month, start_date.day)
    deposit = monthly_rent * 2

    # deliberately omit NIF, Finanças, governing law
    content = [
        f"# CONTRATO DE ARRENDAMENTO COMERCIAL",
        f"# Referência: PT-{idx:04d}-MISSING",
        "---",
        f"Celebrado em {start_date.strftime('%d de %B de %Y')}, entre:",
        f"<b>SENHORIO:</b> {landlord}, com sede em Lisboa (\"Senhorio\");",
        f"<b>ARRENDATÁRIO:</b> {tenant}, com sede em {city} (\"Arrendatário\").",
        "## 1. OBJECTO",
        f"Arrendamento de espaço de escritório em {street}, {postcode} {city}, "
        f"com {sqm} m².",
        "## 2. PRAZO",
        f"Início: {start_date.isoformat()}. Fim: {end_date.isoformat()}.",
        "## 3. RENDA",
        f"Renda mensal: EUR {monthly_rent:,.0f}, pagável no primeiro dia de cada mês.",
        "## 4. DEPÓSITO",
        f"Depósito de garantia: EUR {deposit:,.0f}.",
        "## 5. USO",
        f"Uso exclusivo de escritório.",
        "## 6. OBRIGAÇÕES DAS PARTES",
        f"O Arrendatário obriga-se a conservar o espaço e pagar a renda atempadamente. "
        f"O Senhorio obriga-se a manter o imóvel em condições de habitabilidade.",
        "---",
        f"Assinado em {city}, {start_date.isoformat()}.",
    ]

    gt_base = {
        "filename": f"PT_{idx:04d}_missing_fields_{city.replace(' ', '_')}.pdf",
        "category": "missing_mandatory_fields",
        "property_type": prop_type,
        "tenant_name": tenant,
        "landlord_name": landlord,
        "nif_tenant": None,
        "nif_landlord": None,
        "property_address": f"{street}, {postcode} {city}, Portugal",
        "lease_commencement_date": start_date.isoformat(),
        "lease_expiry_date": end_date.isoformat(),
        "rent_amount": f"EUR {monthly_rent:,.0f} per month",
        "break_option_date": None,
        "rent_review_mechanism": None,
        "security_deposit_months": 2,
        "financas_registration": "no",
        "stamp_duty_party": "not stated",
        "governing_law": "not stated",
        "expected_flags": "missing_nif|missing_financas|missing_governing_law",
        "expected_risk_level": "high",
        "has_nif_tenant": "no",
        "has_nif_landlord": "no",
        "has_financas_clause": "no",
        "assignment_absolute_prohibition": "no",
        "upward_only_review": "no",
        "stamp_duty_on_tenant": "no",
        "notice_below_statutory": "no",
        "deposit_above_6_months": "no",
    }
    return content, gt_base


def build_short_term_lease(idx: int) -> dict:
    """Short-term lease (under 1 year) with correct shorter notice periods."""
    base_content, gt = build_standard_lease(
        random.choice(["retail", "office"]), "short_term", idx
    )
    # override dates to under 1 year
    start = random_date(2023, 2024)
    end = date(start.year, start.month + 9 if start.month <= 3 else start.month - 3,
               start.day)
    if end <= start:
        end = date(start.year + 1, start.month, start.day) - timedelta(days=30)

    for i, line in enumerate(base_content):
        if "prazo do arrendamento inicia-se" in line:
            base_content[i] = (
                f"O prazo do arrendamento inicia-se em {start.isoformat()} "
                f"e termina em {end.isoformat()}, pelo período de 9 meses. "
                f"O contrato não se renova automaticamente."
            )
        if "PRAZOS DE AVISO PRÉVIO" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("Para efeitos"):
                    base_content[j] = (
                        "Para efeitos de resolução: (a) o Arrendatário deve notificar "
                        "o Senhorio com antecedência de 60 dias; (b) o Senhorio deve "
                        "notificar o Arrendatário com antecedência de 60 dias."
                    )
                    break
            break

    gt["category"] = "short_term"
    gt["lease_commencement_date"] = start.isoformat()
    gt["lease_expiry_date"] = end.isoformat()
    gt["notice_period_tenant_days"] = 60
    gt["notice_period_landlord_days"] = 60
    gt["break_option_date"] = None
    gt["expected_flags"] = "none"
    gt["expected_risk_level"] = "low"
    return base_content, gt


def build_high_risk_lease(idx: int) -> dict:
    """High-risk lease: unlimited guarantor + absolute assignment + dilapidations."""
    base_content, gt = build_standard_lease("office", "high_risk", idx)
    tenant = gt["tenant_name"]
    guarantor_nif = random_nif()

    # inject guarantor clause
    base_content.insert(4, (
        f"<b>GARANTE:</b> {tenant.replace('Lda.', 'Group B.V.').replace('S.A.', 'International B.V.')}, "
        f"empresa incorporada nos Países Baixos, com NIF {guarantor_nif} "
        f"(\"Garante\"), que garantia de forma incondicional e irrevogável todas as "
        f"obrigações do Arrendatário ao abrigo do presente Contrato, "
        f"<b>com responsabilidade ilimitada e sem benefício de excussão prévia.</b>"
    ))

    # make assignment absolute prohibition
    for i, line in enumerate(base_content):
        if "CESSÃO E SUBARRENDAMENTO" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("O Arrendatário"):
                    base_content[j] = (
                        "<b>A cessão e subarrendamento são absolutamente proibidos "
                        "em quaisquer circunstâncias, incluindo transmissão de "
                        "estabelecimento comercial.</b>"
                    )
                    break
            break

    # add dilapidations survival
    for i, line in enumerate(base_content):
        if "OPÇÃO DE RESOLUÇÃO ANTECIPADA" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("O Arrendatário"):
                    base_content[j] += (
                        " <b>O exercício da opção de resolução não extingue a "
                        "responsabilidade por obras de conservação e reposição do "
                        "estado original, mantendo-se o Senhorio com o direito de "
                        "reclamar os respectivos custos após a desocupação.</b>"
                    )
                    break
            break

    gt["category"] = "high_risk_combination"
    gt["expected_flags"] = (
        "unlimited_guarantor|absolute_assignment_prohibition|"
        "dilapidations_survival_on_break"
    )
    gt["expected_risk_level"] = "high"
    gt["assignment_absolute_prohibition"] = "yes"
    return base_content, gt


def build_compliance_issue_lease(idx: int) -> dict:
    """Lease with Portugal compliance issues: stamp duty on tenant, short notice."""
    base_content, gt = build_standard_lease(
        random.choice(["retail", "warehouse"]), "compliance_issue", idx
    )
    monthly_rent_val = int(gt["rent_amount"].split()[1].replace(",", ""))

    for i, line in enumerate(base_content):
        if "IMPOSTO DO SELO" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("O Imposto"):
                    base_content[j] = (
                        f"<b>O Imposto do Selo, no valor de "
                        f"EUR {monthly_rent_val * 0.10:,.0f}, é da exclusiva "
                        f"responsabilidade do Arrendatário</b>, que se obriga a "
                        f"efectuar o respectivo pagamento à Autoridade Tributária "
                        f"no prazo legalmente previsto."
                    )
                    break
            break

    for i, line in enumerate(base_content):
        if "PRAZOS DE AVISO PRÉVIO" in line:
            for j in range(i+1, min(i+3, len(base_content))):
                if base_content[j].startswith("Para efeitos"):
                    base_content[j] = (
                        "Para efeitos de resolução ou oposição à renovação: "
                        "(a) o Arrendatário deve notificar o Senhorio com antecedência "
                        "de <b>30 (trinta) dias</b>; (b) o Senhorio deve notificar o "
                        "Arrendatário com antecedência de 60 dias."
                    )
                    break
            break

    gt["category"] = "compliance_issue"
    gt["stamp_duty_party"] = "tenant (non-compliant)"
    gt["notice_period_tenant_days"] = 30
    gt["stamp_duty_on_tenant"] = "yes"
    gt["notice_below_statutory"] = "yes"
    gt["expected_flags"] = "stamp_duty_on_tenant|notice_period_below_statutory"
    gt["expected_risk_level"] = "high"
    return base_content, gt


# ── main generator ────────────────────────────────────────────────────────────

def generate_all(count: int = 200):
    all_ground_truth = []
    idx = 1

    # category distribution
    plan = [
        ("standard_office",    30, lambda i: build_standard_lease("office", "standard_office", i)),
        ("standard_retail",    25, lambda i: build_standard_lease("retail", "standard_retail", i)),
        ("standard_warehouse", 20, lambda i: build_standard_lease("warehouse", "standard_warehouse", i)),
        ("break_option",       25, lambda i: build_break_option_lease(i)),
        ("unusual_rent",       20, lambda i: build_rent_review_lease(i)),
        ("assignment",         20, lambda i: build_assignment_restriction_lease(i)),
        ("missing_fields",     15, lambda i: build_missing_fields_lease(i)),
        ("short_term",         15, lambda i: build_short_term_lease(i)),
        ("high_risk",          15, lambda i: build_high_risk_lease(i)),
        ("compliance_issue",   15, lambda i: build_compliance_issue_lease(i)),
    ]

    for category, n, builder in plan:
        for _ in range(n):
            content, gt = builder(idx)
            filepath = OUTPUT_DIR / gt["filename"]
            make_pdf(filepath, content)
            all_ground_truth.append(gt)
            if idx % 10 == 0:
                print(f"  Generated {idx} leases...")
            idx += 1
            if idx > count:
                break
        if idx > count:
            break

    # write ground truth CSV
    csv_path = OUTPUT_DIR / "ground_truth.csv"
    if all_ground_truth:
        fieldnames = list(all_ground_truth[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_ground_truth)

    print(f"\n✓ Generated {idx-1} lease PDFs in {OUTPUT_DIR}")
    print(f"✓ Ground truth saved to {csv_path}")
    print(f"\nDistribution:")
    from collections import Counter
    cats = Counter(gt["category"] for gt in all_ground_truth)
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    print("Generating 200 synthetic Portuguese commercial leases...")
    generate_all(200)
