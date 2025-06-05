# Sistema de RH - Gestão de Vagas (hr_system)

Este é um projeto Django desenvolvido para gerenciar o processo de cadastro e seleção de vagas em um ambiente hospitalar, com foco na flexibilidade de campos por tipo de vaga.

## Funcionalidades Implementadas (Versão Inicial)

*   **Gestão de Vagas:** Criação, edição e visualização de vagas, associadas a unidades hospitalares e setores.
*   **Tipos de Vaga Dinâmicos:** Criação de diferentes tipos de vaga (ex: Enfermeiro, Técnico, Médico) com a capacidade de definir quais campos específicos aparecerão no formulário de candidatura para cada tipo, através de uma configuração JSON no painel administrativo.
*   **Fluxo do Candidato:**
    *   Visualização de vagas abertas.
    *   Visualização de detalhes da vaga.
    *   Candidatura a vagas com formulário dinâmico (campos variam por tipo de vaga).
    *   Criação/Edição de perfil básico (incluindo upload de CV).
    *   Visualização do histórico de candidaturas.
*   **Fluxo do Recrutador:**
    *   Dashboard com visão geral das vagas.
    *   Listagem de candidatos por vaga, com filtros e ordenação.
    *   Visualização detalhada da candidatura (incluindo dados do formulário dinâmico e CV).
    *   Alteração do status da candidatura.
    *   Agendamento de entrevistas (básico).
*   **Painel Administrativo (Django Admin):**
    *   Gerenciamento completo de Unidades Hospitalares, Setores, Tipos de Vaga (com editor JSON para configuração de campos), Vagas, Candidatos, Candidaturas, Entrevistas, Usuários e Grupos.
*   **Funcionalidades Adicionais:**
    *   Upload de CV no perfil do candidato.
    *   Notificações básicas para candidatos (recebimento de candidatura, mudança de status, agendamento de entrevista).
    *   Log de atividades básicas (candidatura, mudança de status, agendamento de entrevista).

## Estrutura do Projeto

```
/home/ubuntu/hr_system/
├── accounts/         # App para usuários, perfis de candidato
│   ├── migrations/
│   ├── templates/
│   │   └── accounts/
│   │       ├── my_applications.html
│   │       ├── profile_edit.html
│   │       └── profile_view.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core/             # App para modelos/funcionalidades centrais, página inicial
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   └── core/
│   │       └── home.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── hr_system/        # Configurações do projeto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py         # Utilitário de linha de comando do Django
├── media/            # Diretório para arquivos de upload (CVs, Laudos)
├── notifications/    # App para notificações e logs de atividade
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── vacancies/        # App principal para vagas, candidaturas, entrevistas
    ├── migrations/
    ├── templates/
    │   └── vacancies/
    │       ├── already_applied.html
    │       ├── application_success.html
    │       ├── apply_form.html
    │       ├── recruiter_application_detail.html
    │       ├── recruiter_applications_list.html
    │       ├── recruiter_dashboard.html
    │       ├── recruiter_schedule_interview.html
    │       ├── vacancy_detail.html
    │       └── vacancy_list.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

## Como Executar (Ambiente de Desenvolvimento)

1.  **Navegue até o diretório do projeto:**
    ```bash
    cd /home/ubuntu/hr_system
    ```

2.  **Crie um superusuário (administrador) para acessar o Django Admin:**
    ```bash
    python3.11 manage.py createsuperuser
    ```
    Siga as instruções para definir nome de usuário, email e senha.

3.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python3.11 manage.py runserver 0.0.0.0:8000
    ```

4.  **Acesse a aplicação:**
    *   A aplicação estará rodando localmente na porta 8000. Para acessá-la publicamente (de forma temporária), você precisará expor a porta.
    *   **Painel Administrativo:** Acesse `/admin/` e faça login com o superusuário criado.
    *   **Interface Principal:** Acesse a raiz (`/`) ou `/vagas/`.

## Próximos Passos (Sugestões)

*   Implementar autenticação completa (registro, login, logout, recuperação de senha).
*   Adicionar testes automatizados.
*   Refinar a interface do usuário (UI/UX).
*   Implementar funcionalidades de busca e filtros mais avançadas.
*   Criar dashboards e relatórios para recrutadores/administradores.
*   Integrar com sistemas externos (se necessário).
*   Preparar para deploy em produção (configurar servidor web, banco de dados, etc.).

