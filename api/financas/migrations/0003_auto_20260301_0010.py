from django.db import migrations


def criar_icones(apps, schema_editor):
    Icone = apps.get_model('financas', 'Icone')

    icones = [
        ("Pasta+", "pi pi-folder-plus", "Sistema"),
        ("Recibo", "pi pi-receipt", "Financeiro"),
        ("Smile", "pi pi-face-smile", "Pessoal"),
        ("Coroa", "pi pi-crown", "Premium"),
        ("Galpão", "pi pi-warehouse", "Empresarial"),
        ("Cracha", "pi pi-clipboard", "Trabalho"),
        ("Venus", "pi pi-venus", "Pessoal"),
        ("Marte", "pi pi-mars", "Pessoal"),
        ("Compras", "pi pi-cart-minus", "Financeiro"),
        ("CarrinhoDeCompras", "pi pi-shopping-cart", "Financeiro"),
        ("Trofeu", "pi pi-trophy", "Conquistas"),
        ("CodigoBarras", "pi pi-barcode", "Sistema"),
        ("Ethereum", "pi pi-ethereum", "Cripto"),
        ("Lampada", "pi pi-lightbulb", "Ideias"),
        ("Calendário", "pi pi-calendar-clock", "Agenda"),
        ("Alvo", "pi pi-bullseye", "Metas"),
        ("Graduação", "pi pi-graduation-cap", "Educação"),
        ("Martelo", "pi pi-hammer", "Ferramentas"),
        ("Velocimetro", "pi pi-gauge", "Indicadores"),
        ("Headphones", "pi pi-headphones", "Lazer"),
        ("Cronometro", "pi pi-stopwatch", "Tempo"),
        ("Caminhão", "pi pi-truck", "Logística"),
        ("Bitcoin", "pi pi-bitcoin", "Cripto"),
        ("Presente", "pi pi-gift", "Pessoal"),
        ("Calculadora", "pi pi-calculator", "Financeiro"),
        ("Mala", "pi pi-shopping-bag", "Compras"),
        ("Servidor", "pi pi-server", "Tecnologia"),
        ("BancoDeDados", "pi pi-database", "Tecnologia"),
        ("Energia", "pi pi-bolt", "Serviços"),
        ("Caixa", "pi pi-box", "Logística"),
        ("Predio", "pi pi-building", "Empresarial"),
        ("Carro", "pi pi-car", "Transporte"),
        ("CartãoDeCredito", "pi pi-credit-card", "Financeiro"),
        ("Mapa", "pi pi-map", "Localização"),
        ("Carteira", "pi pi-wallet", "Financeiro"),
        ("Bandeira", "pi pi-flag", "Metas"),
        ("Sol", "pi pi-sun", "Clima"),
        ("Livro", "pi pi-book", "Educação"),
        ("Euro", "pi pi-euro", "Financeiro"),
        ("Porcentagem", "pi pi-percentage", "Financeiro"),
        ("Escudo", "pi pi-shield", "Segurança"),
        ("Amazon", "pi pi-amazon", "Marcas"),
        ("Fone", "pi pi-phone", "Comunicação"),
        ("Ticket", "pi pi-ticket", "Eventos"),
        ("Desktop", "pi pi-desktop", "Tecnologia"),
        ("Paleta", "pi pi-palette", "Design"),
        ("Android", "pi pi-android", "Tecnologia"),
        ("Apple", "pi pi-apple", "Tecnologia"),
        ("Microsoft", "pi pi-microsoft", "Tecnologia"),
        ("Chave", "pi pi-key", "Segurança"),
        ("Coração", "pi pi-heart", "Pessoal"),
        ("Mobile", "pi pi-mobile", "Tecnologia"),
        ("PastaTrabalho", "pi pi-briefcase", "Trabalho"),
        ("Dinheiro", "pi pi-money-bill", "Financeiro"),
        ("Imagens", "pi pi-images", "Mídia"),
        ("GraficoBarras", "pi pi-chart-bar", "Indicadores"),
        ("Camera", "pi pi-camera", "Mídia"),
        ("Olho", "pi pi-eye", "Visual"),
        ("Video", "pi pi-video", "Mídia"),
        ("Tags", "pi pi-tags", "Organização"),
        ("Tag", "pi pi-tag", "Organização"),
        ("Calendario+", "pi pi-calendar-plus", "Agenda"),
        ("Globo", "pi pi-globe", "Global"),
        ("Impressora", "pi pi-print", "Escritório"),
        ("Engrenagem", "pi pi-cog", "Sistema"),
        ("Lixo", "pi pi-trash", "Sistema"),
        ("EstrelaCheia", "pi pi-star-fill", "Favoritos"),
        ("Estrela", "pi pi-star", "Favoritos"),
        ("Casa", "pi pi-home", "Pessoal"),
        ("GraficoPizza", "pi pi-chart-pie", "Indicadores"),
        ("Megafone", "pi pi-megaphone", "Marketing"),
        ("Microfone", "pi pi-microphone", "Mídia"),
        ("Línguas", "pi pi-language", "Educação"),
        ("Ampulheta", "pi pi-hourglass", "Tempo"),
        ("Verificado", "pi pi-verified", "Sistema"),
        ("Play", "pi pi-play-circle", "Mídia"),
        ("Pin", "pi pi-thumbtack", "Organização"),
        ("Hashtag", "pi pi-hashtag", "Social"),
        ("Codigo", "pi pi-code", "Tecnologia"),
        ("Sync", "pi pi-sync", "Sistema"),
        ("Asterisco", "pi pi-asterisk", "Sistema"),
        ("Brilho", "pi pi-sparkles", "Premium"),
        ("Lua", "pi pi-moon", "Clima"),
        ("Excel", "pi pi-file-excel", "Arquivos"),
        ("PDF", "pi pi-file-pdf", "Arquivos"),
        ("Imagem", "pi pi-image", "Mídia"),
        ("Lista", "pi pi-list", "Organização"),
        ("OlhoFechado", "pi pi-eye-slash", "Visual"),
    ]

    for nome, classe_css, categoria_visual in icones:
        Icone.objects.get_or_create(
            nome=nome,
            defaults={
                "classe_css": classe_css,
                "categoria_visual": categoria_visual,
                "created_by_id": 1,
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('financas', '0002_icone_alter_categoria_icone_consolidadomensal_meta'),
    ]

    operations = [
        migrations.RunPython(criar_icones),
    ]