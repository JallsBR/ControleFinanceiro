from financas.models import Categoria


def criar_categorias_iniciais(usuario):

    categorias = [
        ("Salário", "E", 2),
        ("Freelance", "E", 75),
        ("Investimentos", "E", 31),
        ("Moradia", "S", 7),
        ("Alimentação", "S", 5),
        ("Supermercado", "S", 12),
        ("Farmácia", "S", 53),
        ("Transporte", "S", 21),
        ("Saúde", "S", 43),
        ("Educação", "S", 76),
        ("Lazer", "S", 83),
        ("Impostos", "S", 14),
        ("Outros", "S", 88),
    ]
    for nome, tipo, icone_id in categorias:
        Categoria.objects.create(
            created_by=usuario,
            nome=nome,
            tipo=tipo,
            icone_id=icone_id,
        )
