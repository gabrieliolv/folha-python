create table if not exists cargos (
    id bigserial primary key,
    nome_cargo text not null unique,
    salario_base numeric(12,2)
);

alter table lojas
    add column if not exists apelido text,
    add column if not exists empresa text,
    add column if not exists cnpj text,
    add column if not exists endereco text,
    add column if not exists contato text;

alter table funcionarios
    add column if not exists cargo_id bigint references cargos(id),
    add column if not exists carga_horaria_dia_semana numeric(6,2) default 8,
    add column if not exists desconto_vt boolean default false,
    add column if not exists desconto_va_vr boolean default false,
    add column if not exists percentual_vt numeric(5,2) default 0,
    add column if not exists percentual_va_vr numeric(5,2) default 0,
    add column if not exists outros_descontos numeric(12,2) default 0,
    add column if not exists data_admissao date,
    add column if not exists contato text,
    add column if not exists email text,
    add column if not exists tipo_pagamento text check (tipo_pagamento in ('PIX','BANCO')),
    add column if not exists chave_pix text,
    add column if not exists dados_bancarios jsonb;

create table if not exists folha_ponto (
    id bigserial primary key,
    funcionario_id bigint not null references funcionarios(id),
    mes_referencia date not null,
    horas_trabalhadas numeric(8,2) default 0,
    faltas_horas numeric(8,2) default 0,
    atestados_horas numeric(8,2) default 0,
    banco_horas numeric(8,2) default 0,
    horas_extras numeric(8,2) default 0,
    desconto_dsr_horas numeric(8,2) default 0,
    created_at timestamptz default now()
);

create table if not exists auditoria_logs (
    id bigserial primary key,
    usuario text not null,
    acao text not null,
    tabela text not null,
    registro_id text,
    payload jsonb,
    created_at timestamptz default now()
);

alter table if exists usuarios
    add column if not exists tipo text default 'USER';
