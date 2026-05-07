from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import hashlib


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIA
# ─────────────────────────────────────────────────────────────────────────────

class Categoria(models.Model):

    class Tipo(models.TextChoices):
        RECEITA = "RECEITA", "Receita"
        DESPESA = "DESPESA", "Despesa"

    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        blank=True,
        null=True,
        verbose_name="Tipo",
    )
    pai = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategorias",
        verbose_name="Categoria Pai",
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# ─────────────────────────────────────────────────────────────────────────────
# MEIO DE PAGAMENTO
# ─────────────────────────────────────────────────────────────────────────────

class MeioDePagamento(models.Model):

    class Tipo(models.TextChoices):
        CREDITO       = "CREDITO",       "Cartão de Crédito"
        DEBITO        = "DEBITO",        "Cartão de Débito"
        PIX           = "PIX",           "PIX"
        BOLETO        = "BOLETO",        "Boleto Bancário"
        DINHEIRO      = "DINHEIRO",      "Dinheiro Físico"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferência"
        CHEQUE        = "CHEQUE",        "Cheque"
        OUTRO         = "OUTRO",         "Outro"

    nome = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome amigável para identificar",
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.CREDITO,
        verbose_name="Tipo",
    )
    descricao = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descrição")

    instituicao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instituição")

    numero_final = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Número Final",
        help_text="Últimos dígitos do cartão",
    )

    bandeira = models.CharField(max_length=20, blank=True, null=True, verbose_name="Bandeira")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Meio de Pagamento"
        verbose_name_plural = "Meios de Pagamento"
        ordering = ["nome"]
        unique_together = [["nome", "tipo"]]

    def __str__(self):
        if self.numero_final:
            return f"{self.nome} ({self.get_tipo_display()}) - ****{self.numero_final}"
        return f"{self.nome} ({self.get_tipo_display()})"


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACAO
# ─────────────────────────────────────────────────────────────────────────────

class Transacao(models.Model):

    class TipoParcela(models.TextChoices):
        UNICA     = "UNICA",     "Única"
        PARCELADA = "PARCELADA", "Parcelada"

    class QuemPagou(models.TextChoices):
        GUILHERME = "Guilherme", "Guilherme"
        PAULA     = "Paula",     "Paula"

    # ── datas e identificação ─────────────────────────────────────────────────
    data_compra = models.DateField(verbose_name="Data de Compra")
    data_base = models.CharField(
        max_length=6,
        verbose_name="Data Base",
        help_text="Período de referência da carga. Formato: AAAAMM — ex: 202603",
    )
    if_instituicao = models.CharField(
        max_length=100,
        default="Banco C6",
        verbose_name="Instituição Financeira (IF)",
    )

    # ── relacionamentos ───────────────────────────────────────────────────────
    meio_pagamento = models.ForeignKey(
        MeioDePagamento,
        on_delete=models.PROTECT,       # PROTECT: impede deleção acidental do meio de pagamento
        verbose_name="Meio de Pagamento",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,       # PROTECT: impede deleção acidental da categoria
        verbose_name="Categoria",
    )

    # ── descrição ─────────────────────────────────────────────────────────────
    descricao = models.CharField(max_length=200, verbose_name="Descrição")

    # ── parcelamento ──────────────────────────────────────────────────────────
    tipo_parcela = models.CharField(
        max_length=10,
        choices=TipoParcela.choices,
        default=TipoParcela.UNICA,
        verbose_name="Tipo de Parcela",
    )
    parcela_atual = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Parcela Atual",
        help_text="Ex: 9 (de 9/11)",
    )
    total_parcelas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Total de Parcelas",
        help_text="Ex: 11 (de 9/11)",
    )

    # ── valores ───────────────────────────────────────────────────────────────
    valor_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Valor (em US$)",
    )
    cotacao = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("0"),
        verbose_name="Cotação (em R$)",
    )
    valor_brl = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor (em R$)",
    )

    # ── split ─────────────────────────────────────────────────────────────────
    split_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Split (%)",
        help_text="Percentual do rateio. Default: 50 %",
    )
    valor_split = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        verbose_name="Valor Split (R$)",
        help_text="Calculado automaticamente: valor_brl × split_percent / 100",
    )
    quem_pagou = models.CharField(
        max_length=50,
        choices=QuemPagou.choices,
        default=QuemPagou.GUILHERME,
        verbose_name="Quem Pagou",
    )

    # ── deduplicação ──────────────────────────────────────────────────────────
    hash_linha = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="Hash da Linha (SHA-256)",
        help_text=(
            "SHA-256 dos campos originais do CSV. "
            "Garante que a mesma transação nunca seja inserida duas vezes, "
            "mesmo que o arquivo seja reprocessado ou renomeado."
        ),
    )

    # ── rastreabilidade ───────────────────────────────────────────────────────
    arquivo_origem = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Arquivo de Origem",
        help_text="Nome do arquivo CSV que gerou este registro",
    )

    # ── auditoria ─────────────────────────────────────────────────────────────
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # ── meta ──────────────────────────────────────────────────────────────────
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ["-data_compra", "descricao"]
        indexes = [
            models.Index(fields=["data_base"],                    name="idx_transacao_data_base"),
            models.Index(fields=["data_compra"],                  name="idx_transacao_data_compra"),
            models.Index(fields=["meio_pagamento", "data_compra"],name="idx_transacao_meio_data"),
            models.Index(fields=["quem_pagou"],                   name="idx_transacao_quem_pagou"),
            # hash_linha já tem índice implícito pelo unique=True
        ]

    # ── lógica de negócio ─────────────────────────────────────────────────────
    @staticmethod
    def calcular_hash(
        data_compra: str,
        descricao: str,
        parcela_atual: str,
        total_parcelas: str,
        valor_brl: str,
        numero_final: str,
    ) -> str:
        """
        Gera SHA-256 a partir dos campos que identificam unicamente
        uma transação no CSV original.

        Uso no serviço de carga (strings cruas do CSV, antes do parse):
            hash_linha = Transacao.calcular_hash(
                data_compra   = "21/08/2025",
                descricao     = "40+ ACADEMIA",
                parcela_atual = "9",
                total_parcelas= "11",
                valor_brl     = "550.00",
                numero_final  = "3680",
            )
        """
        partes = [
            str(data_compra).strip().upper(),
            str(descricao).strip().upper(),
            str(parcela_atual).strip(),
            str(total_parcelas).strip(),
            str(valor_brl).strip(),
            str(numero_final).strip(),
        ]
        payload = "|".join(partes).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def calcular_valor_split(self) -> Decimal:
        """Calcula valor_split com precisão Decimal."""
        return (
            self.valor_brl * self.split_percent / Decimal("100")
        ).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.valor_split = self.calcular_valor_split()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data_compra} | {self.descricao} | R$ {self.valor_brl}"


# ─────────────────────────────────────────────────────────────────────────────
# LOG DE CARGA
# ─────────────────────────────────────────────────────────────────────────────

class LogCarga(models.Model):
    """
    Registra cada execução de carga de CSV.
    Um registro por arquivo importado.

    hash_arquivo bloqueia reprocessamento do mesmo arquivo,
    mesmo que seja renomeado.
    """

    data_base = models.CharField(max_length=6, verbose_name="Data Base (AAAAMM)")
    if_instituicao = models.CharField(max_length=100, default="Banco C6", verbose_name="IF")
    arquivo_nome = models.CharField(max_length=255, verbose_name="Arquivo")
    split_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        verbose_name="Split (%) usado na carga",
    )

    # ── deduplicação de arquivo ───────────────────────────────────────────────
    hash_arquivo = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="Hash do Arquivo (SHA-256)",
        help_text="Impede que o mesmo arquivo seja importado mais de uma vez.",
    )

    # ── resultados ────────────────────────────────────────────────────────────
    total_linhas      = models.IntegerField(default=0, verbose_name="Total de Linhas")
    total_importadas  = models.IntegerField(default=0, verbose_name="Importadas")
    total_duplicadas  = models.IntegerField(default=0, verbose_name="Duplicatas Ignoradas")
    total_erros       = models.IntegerField(default=0, verbose_name="Erros")
    erros_detalhe     = models.TextField(blank=True, null=True, verbose_name="Detalhe dos Erros")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Carga"
        verbose_name_plural = "Logs de Carga"
        ordering = ["-criado_em"]

    @staticmethod
    def calcular_hash_arquivo(caminho: str) -> str:
        """
        Gera SHA-256 do conteúdo binário do arquivo CSV.

        Uso no serviço de carga (antes de qualquer processamento):
            hash_arq = LogCarga.calcular_hash_arquivo("fatura.csv")
            if LogCarga.objects.filter(hash_arquivo=hash_arq).exists():
                raise ValueError("Arquivo já foi importado anteriormente.")
        """
        h = hashlib.sha256()
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                h.update(bloco)
        return h.hexdigest()

    def __str__(self):
        return (
            f"Carga {self.data_base} | {self.arquivo_nome} | "
            f"{self.total_importadas} importadas / "
            f"{self.total_duplicadas} duplicatas / "
            f"{self.total_erros} erros"
        )