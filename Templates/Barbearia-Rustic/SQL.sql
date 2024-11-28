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
    nome_cliente VARCHAR(100) NOT NULL,
    senha_cliente VARCHAR(255) NOT NULL,
    contato_cliente VARCHAR(15) NOT NULL,
    email_cliente VARCHAR(100) NOT NULL,
    barbeiro_selecionado VARCHAR(100) NOT NULL,
    data DATE NOT NULL,
    horario TIME NOT NULL,
    servico VARCHAR(100) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
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

CREATE TABLE barbeiros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO barbeiros (nome, email, senha) VALUES
('João Silva', 'joao@barbeiro.com', '123456'),
('Carlos Pereira', 'carlos@barbeiro.com', '123456'),
('Lucas Oliveira', 'lucas@barbeiro.com', '123456'),
('Rafael Santos', 'rafael@barbeiro.com', '123456'),
('André Almeida', 'andre@barbeiro.com', '123456'),
('Gabriel Pires', 'gabriel@barbeiro.com', '123456'),
('Miguel Andrade', 'miguel@barbeiro.com', '123456'),
('Henrique Oliveira', 'henrique@barbeiro.com', '123456');
select*from barbeiros;

drop table barbeiros;

CREATE TABLE cronograma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barbeiro_id INT,
    data DATE,
    horario TIME,
    status ENUM('disponivel', 'ocupado') DEFAULT 'disponivel',
    FOREIGN KEY (barbeiro_id) REFERENCES funcionarios(id)
);
select*from cronograma;

drop table cronograma;