
CREATE DATABASE IF NOT EXISTS barbearia;

USE barbearia;

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    contato VARCHAR(15) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select*from clientes;

drop table clientes;

CREATE TABLE agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_cliente VARCHAR(100),
    contato_cliente VARCHAR(15),
    email_cliente VARCHAR(100),
    data DATE,
    horario TIME,
    servico VARCHAR(100),
    valor DECIMAL(10, 2),
    data_agendamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select*from agendamentos;

drop table agendamentos;

CREATE TABLE feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    comentario TEXT,
    nivel_satisfacao INT
);
select*from feedbacks;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'cliente', 'barbeiro') NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO usuarios (nome, email, senha, tipo) VALUES 
('Admin User', 'admin@barbearia.com', '<senha_hash_admin>', 'admin'),
('Cliente User', 'cliente@barbearia.com', '<senha_hash_cliente>', 'cliente'),
('Barbeiro User', 'barbeiro@barbearia.com', '<senha_hash_barbeiro>', 'barbeiro');

select*from usuarios;

