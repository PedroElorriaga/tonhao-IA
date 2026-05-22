-- =============================================================
-- Seed data for tonhao.db
-- Passwords: Tonhao@123
-- Run with: sqlite3 tonhao.db < seed.sql
-- =============================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- users
-- -----------------------------------------------------------
INSERT OR IGNORE INTO users (id, email, name, hashed_password, google_id, role, created_at) VALUES
  ('aaaaaaaa-0001-0001-0001-000000000001', 'admin@tonhao.dev',         'Admin Tonhão',  '$2a$12$MXUA6Zw7CoIKuv27XNH5I..jg1TEMGtH0nkzqgAYu/Tb77C7V7A8a', NULL, 'agent',  '2025-01-01 09:00:00'),
  ('aaaaaaaa-0002-0002-0002-000000000002', 'maria@empresa.com',  'Maria Silva',   '$2a$12$MXUA6Zw7CoIKuv27XNH5I..jg1TEMGtH0nkzqgAYu/Tb77C7V7A8a', NULL, 'agent',  '2025-01-05 09:00:00'),
  ('bbbbbbbb-0001-0001-0001-000000000001', 'joao@cliente.com',   'João Souza',    '$2a$12$MXUA6Zw7CoIKuv27XNH5I..jg1TEMGtH0nkzqgAYu/Tb77C7V7A8a', NULL, 'client', '2025-02-10 09:00:00'),
  ('bbbbbbbb-0002-0002-0002-000000000002', 'ana@cliente.com',    'Ana Costa',     '$2a$12$MXUA6Zw7CoIKuv27XNH5I..jg1TEMGtH0nkzqgAYu/Tb77C7V7A8a', NULL, 'client', '2025-03-15 09:00:00'),
  ('bbbbbbbb-0003-0003-0003-000000000003', 'carlos@cliente.com',  'Carlos Lima',   '$2a$12$MXUA6Zw7CoIKuv27XNH5I..jg1TEMGtH0nkzqgAYu/Tb77C7V7A8a', NULL, 'client', '2025-04-20 09:00:00');

-- -----------------------------------------------------------
-- tickets
-- -----------------------------------------------------------
INSERT OR IGNORE INTO tickets (id, title, description, status, priority, category, client_name, created_at, updated_at, attachment_url, attachment_name) VALUES
  ('cccccccc-0001-0001-0001-000000000001',
   'Não consigo acessar o sistema',
   'Ao tentar fazer login, recebo a mensagem ''Credenciais inválidas'', mas tenho certeza que a senha está correta.',
   'open', 'high', 'Technical Support', 'João Souza',
   '2026-05-01 09:30:00', NULL, NULL, NULL),

  ('cccccccc-0002-0002-0002-000000000002',
   'Cobrança duplicada na fatura de abril',
   'Identificiei duas cobranças de R$ 299,90 referentes ao mês de abril. Solicito estorno de uma delas.',
   'in_progress', 'critical', 'Billing', 'Ana Costa',
   '2026-05-03 14:00:00', '2026-05-04 10:00:00', NULL, NULL),

  ('cccccccc-0003-0003-0003-000000000003',
   'Dúvida sobre política de férias',
   'Gostaria de saber quantos dias de férias acumulo por ano e como solicitar o período.',
   'solved', 'low', 'HR', 'Carlos Lima',
   '2026-04-20 11:00:00', '2026-04-21 09:00:00', NULL, NULL),

  ('cccccccc-0004-0004-0004-000000000004',
   'Lentidão no carregamento do dashboard',
   'O painel principal demora mais de 30 segundos para carregar. O problema ocorre em todos os navegadores.',
   'pending', 'medium', 'Technical Support', 'João Souza',
   '2026-05-10 08:00:00', '2026-05-10 16:00:00', NULL, NULL),

  ('cccccccc-0005-0005-0005-000000000005',
   'Como alterar o e-mail cadastrado?',
   'Preciso atualizar meu e-mail de contato no sistema para um novo endereço corporativo.',
   'open', 'low', 'General', 'Ana Costa',
   '2026-05-12 15:30:00', NULL, NULL, NULL),

  ('cccccccc-0006-0006-0006-000000000006',
   'Erro 500 ao exportar relatório',
   'Ao clicar em ''Exportar CSV'' na tela de relatórios, o sistema retorna erro interno do servidor.',
   'open', 'high', 'Technical Support', 'Carlos Lima',
   '2026-05-15 10:15:00', NULL, NULL, NULL),

  ('cccccccc-0007-0007-0007-000000000007',
   'Cancelamento de assinatura',
   'Gostaria de cancelar minha assinatura mensal e entender o procedimento de reembolso proporcional.',
   'closed', 'medium', 'Billing', 'João Souza',
   '2026-04-05 09:00:00', '2026-04-07 17:00:00', NULL, NULL),

  ('cccccccc-0008-0008-0008-000000000008',
   'Solicitação de treinamento no sistema',
   'Nossa equipe é nova e precisa de um treinamento guiado para utilizar as principais funcionalidades.',
   'pending', 'medium', 'General', 'Ana Costa',
   '2026-05-18 13:00:00', '2026-05-19 09:00:00', NULL, NULL);

-- -----------------------------------------------------------
-- ticket_replies
-- -----------------------------------------------------------
INSERT OR IGNORE INTO ticket_replies (id, ticket_id, author, body, is_ai, created_at) VALUES
  -- Ticket 1: login issue
  ('dddddddd-0001-0001-0001-000000000001', 'cccccccc-0001-0001-0001-000000000001',
   'TonhãoIA',
   'Olá, João! Identificamos que sua conta pode estar com bloqueio temporário após múltiplas tentativas de login. Tente redefinir sua senha clicando em ''Esqueci minha senha'' na tela de login. Caso o problema persista, um agente humano entrará em contato.',
   1, '2026-05-01 09:31:00'),

  ('dddddddd-0002-0002-0002-000000000002', 'cccccccc-0001-0001-0001-000000000001',
   'João Souza',
   'Tentei redefinir mas não recebi o e-mail de recuperação.',
   0, '2026-05-01 10:05:00'),

  -- Ticket 2: billing duplicate
  ('dddddddd-0003-0003-0003-000000000003', 'cccccccc-0002-0002-0002-000000000002',
   'TonhãoIA',
   'Olá, Ana! Lamentamos o inconveniente. Abrimos uma análise financeira para verificar a cobrança duplicada. O prazo para estorno é de até 5 dias úteis após confirmação. Aguarde contato da nossa equipe de faturamento.',
   1, '2026-05-03 14:01:00'),

  ('dddddddd-0004-0004-0004-000000000004', 'cccccccc-0002-0002-0002-000000000002',
   'Maria Silva',
   'Ana, confirmamos a cobrança duplicada. O estorno foi solicitado e deve aparecer em sua fatura em até 3 dias úteis.',
   0, '2026-05-04 10:00:00'),

  -- Ticket 3: HR vacation
  ('dddddddd-0005-0005-0005-000000000005', 'cccccccc-0003-0003-0003-000000000003',
   'TonhãoIA',
   'Olá, Carlos! De acordo com nossa política de RH, colaboradores acumulam 30 dias de férias a cada 12 meses de trabalho. Para solicitar o período, acesse o portal de RH > Férias > Nova Solicitação, com ao menos 30 dias de antecedência.',
   1, '2026-04-20 11:01:00'),

  ('dddddddd-0006-0006-0006-000000000006', 'cccccccc-0003-0003-0003-000000000003',
   'Carlos Lima',
   'Perfeito, obrigado pela informação!',
   0, '2026-04-20 11:30:00'),

  ('dddddddd-0007-0007-0007-000000000007', 'cccccccc-0003-0003-0003-000000000003',
   'Admin Tonhão',
   'Ticket encerrado com solução confirmada pelo cliente.',
   0, '2026-04-21 09:00:00'),

  -- Ticket 4: dashboard slow
  ('dddddddd-0008-0008-0008-000000000008', 'cccccccc-0004-0004-0004-000000000004',
   'TonhãoIA',
   'Olá! A lentidão pode estar relacionada a cache desatualizado ou volume elevado de dados. Recomendamos limpar o cache do navegador (Ctrl+Shift+Del) e tentar novamente. Nossa equipe técnica também irá investigar o desempenho do servidor.',
   1, '2026-05-10 08:01:00'),

  -- Ticket 7: cancellation
  ('dddddddd-0009-0009-0009-000000000009', 'cccccccc-0007-0007-0007-000000000007',
   'TonhãoIA',
   'Olá, João! Recebemos sua solicitação de cancelamento. O reembolso proporcional é calculado com base nos dias restantes do mês vigente. Nosso time de faturamento processará o pedido em até 2 dias úteis.',
   1, '2026-04-05 09:01:00'),

  ('dddddddd-0010-0010-0010-000000000010', 'cccccccc-0007-0007-0007-000000000007',
   'Maria Silva',
   'Cancelamento processado. Reembolso de R$ 150,00 creditado no cartão final 1234.',
   0, '2026-04-07 17:00:00');
