-- Estrutura do banco de dados (SQLite). Uma linha = uma leitura de um módulo em um ciclo.
CREATE TABLE IF NOT EXISTS registros (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_modulo     TEXT    NOT NULL,                       -- ex.: MOD-EN-001
    modulo            TEXT    NOT NULL,                       -- nome do módulo
    tipo              TEXT    NOT NULL,                       -- energia, habitação, ...
    ciclo             INTEGER NOT NULL CHECK (ciclo > 0),     -- ciclo de operação
    consumo_kwh       REAL    NOT NULL CHECK (consumo_kwh >= 0),
    geracao_kwh       REAL    NOT NULL DEFAULT 0 CHECK (geracao_kwh >= 0),
    bateria_pct       REAL    NOT NULL CHECK (bateria_pct BETWEEN 0 AND 100),
    temperatura_c     REAL    NOT NULL,
    ocupacao_pct      REAL    NOT NULL CHECK (ocupacao_pct BETWEEN 0 AND 100),
    status            TEXT    NOT NULL CHECK (status IN ('ativo', 'manutenção', 'alerta')),
    prioridade_alerta INTEGER NOT NULL CHECK (prioridade_alerta BETWEEN 1 AND 5),
    mensagem          TEXT,
    UNIQUE (codigo_modulo, ciclo)                             -- um módulo só tem 1 leitura por ciclo
);
