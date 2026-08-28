import os

_LANGUAGES = {
    "pt_BR": {
        "The shelf is empty.": "A prateleira está vazia.",
        "Just now": "Agora mesmo",
        "{}m ago": "há {}m",
        "{}h ago": "há {}h",
        "{}d ago": "há {}d",
        "Copy": "Copiar",
        "Folder": "Pasta",
        "1 file": "1 arquivo",
        "{} files": "{} arquivos",
        "... and {} more": "... e mais {}",
        "Search...": "Pesquisar...",
        "Open link in browser": "Abrir link no navegador",
        "Open folder": "Abrir pasta",
        "Waiting for key...": "Aguardando tecla...",
        "Global Hotkey (Click to capture)": "Atalho Global (Clique p/ capturar)",
        "Right Edge": "Borda Direita",
        "Left Edge": "Borda Esquerda",
        "Click to redefine hotkey": "Clique para redefinir o atalho",
        "Settings": "Configurações",
        "Accent Color": "Cor Destaque",
        "Sound Effects": "Efeitos Sonoros",
        "Quit Py-Drop completely": "Encerrar o Py-Drop completamente",
        "Pin item": "Fixar item",
        "Translucent Background": "Fundo Translúcido",
        "Background Opacity (%)": "Opacidade do Fundo (%)",
        "Language": "Idioma",
        "Pinned Items": "Itens Fixados",
        "Edge Side": "Lado da Borda",
        "Edge Side for this monitor": "Lado da borda neste monitor",
        "Shelf Width (pixels)": "Largura da Prateleira (pixels)",
        "Clear unpinned items": "Limpar itens não fixados",
        "Clear all unpinned items from the shelf?": "Limpar todos os itens não fixados da prateleira?",
        "No matches found.": "Nenhum resultado encontrado.",
        "Not found": "Não encontrado",
        "Pause/Resume capture": "Pausar/Retomar captura",
        "Restart Application": "Reiniciar Aplicativo",
        "Restart Py-Drop": "Reiniciar o Py-Drop",
        "Remove item": "Remover item",
        "Quit Application": "Sair do Aplicativo",
        "Select All": "Selecionar Tudo",
        "Shelf is empty.": "A prateleira está vazia.",
        "Drop here": "Solte aqui",
        "Drop here to group": "Solte aqui para agrupar",
        "Drop here to ungroup": "Solte aqui para desagrupar",
        "Trigger Area (pixels)": "Área de Ativação (pixels)",
        "Click Behavior (Item)": "Comportamento ao Clicar (Item)",
        "Left-click behavior:": "Comportamento do clique esquerdo:",
        "Copy and Paste in Window": "Copiar e Colar na Janela",
        "Copy Only": "Apenas Copiar",
        "Older": "Antigos",
        "Today": "Hoje",
        "Yesterday": "Ontem",
        "Last 7 days": "Últimos 7 dias",
        "Last 30 days": "Últimos 30 dias",
        "Loading preview...": "Carregando preview...",
        "Appearance": "Aparência",
        "Behavior": "Comportamento",
        "Edge Zone": "Zona da Borda",
        "System": "Sistema",
        "Trigger Height (%)": "Altura de Ativação (%)",
        "Link": "Link",
        "Move clicked item to top": "Mover item clicado para o topo"
    },
    "en_US": {
        # Empty dict or maps to itself
        "The shelf is empty.": "The shelf is empty."
    }
}

_current_lang = "pt_BR"

def set_language(lang_code):
    global _current_lang
    if lang_code in _LANGUAGES:
        _current_lang = lang_code

def tr(text):
    return _LANGUAGES[_current_lang].get(text, text)
