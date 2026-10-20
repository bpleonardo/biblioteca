-- SQL Server

USE [Biblioteca_TEST];

-- ============================================
-- BANCO DE DADOS - SISTEMA DE BIBLIOTECA
-- SQL SERVER (SSMS 20)
-- ============================================

-- 1. EDITORA
CREATE TABLE tb_editora (
    id_editora INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18)
);

-- 2. CATEGORIA
CREATE TABLE tb_categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL
);

-- 3. INSTITUICAO
CREATE TABLE tb_instituicao (
    id_instituicao INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(150) NOT NULL
);

-- 4. CURSO
CREATE TABLE tb_curso (
    id_curso INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_instituicao INT NOT NULL,
    CONSTRAINT fk_tb_curso_instituicao FOREIGN KEY (id_instituicao)
        REFERENCES tb_instituicao(id_instituicao) ON DELETE NO ACTION
);

-- 5. USUARIO
CREATE TABLE tb_usuario (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

-- 6. ALUNO
CREATE TABLE tb_aluno (
    id_aluno INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_curso INT NOT NULL,
    matricula VARCHAR(30),
    CONSTRAINT fk_tb_aluno_usuario FOREIGN KEY (id_usuario)
        REFERENCES tb_usuario(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_tb_aluno_curso FOREIGN KEY (id_curso)
        REFERENCES tb_curso(id_curso) ON DELETE NO ACTION
);

-- 7. AUTORES
CREATE TABLE tb_autores (
    id_autor INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    cpf VARCHAR(14),
    celular VARCHAR(20),
    id_editora INT,
    CONSTRAINT fk_tb_autores_editora FOREIGN KEY (id_editora)
        REFERENCES tb_editora(id_editora) ON DELETE SET NULL
);

-- 8. LIVROS
CREATE TABLE tb_livros (
    id_livro INT IDENTITY(1,1) PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    isbn VARCHAR(20),
    id_categoria INT NOT NULL,
    id_editora INT NOT NULL,
    CONSTRAINT fk_tb_livros_categoria FOREIGN KEY (id_categoria)
        REFERENCES tb_categoria(id_categoria) ON DELETE NO ACTION,
    CONSTRAINT fk_tb_livros_editora FOREIGN KEY (id_editora)
        REFERENCES tb_editora(id_editora) ON DELETE NO ACTION
);

-- 9. LIVROS_AUTORES (TABELA ASSOCIATIVA N:N)
CREATE TABLE tb_livros_autores (
    id_livro INT NOT NULL,
    id_autor INT NOT NULL,
    PRIMARY KEY (id_livro, id_autor),
    CONSTRAINT fk_tb_livrosautores_livro FOREIGN KEY (id_livro)
        REFERENCES tb_livros(id_livro) ON DELETE CASCADE,
    CONSTRAINT fk_tb_livrosautores_autor FOREIGN KEY (id_autor)
        REFERENCES tb_autores(id_autor) ON DELETE CASCADE
);

-- 10. EXEMPLARES
CREATE TABLE tb_exemplares (
    id_exemplar INT IDENTITY(1,1) PRIMARY KEY,
    id_livro INT NOT NULL,
    edicao VARCHAR(30),
    situacao VARCHAR(30),
    CONSTRAINT fk_tb_exemplares_livro FOREIGN KEY (id_livro)
        REFERENCES tb_livros(id_livro) ON DELETE CASCADE
);

-- 11. RESERVA
CREATE TABLE tb_reserva (
    id_reserva INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_livro INT NOT NULL,
    data_reserva DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    situacao VARCHAR(30),
    CONSTRAINT fk_tb_reserva_usuario FOREIGN KEY (id_usuario)
        REFERENCES tb_usuario(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_tb_reserva_livro FOREIGN KEY (id_livro)
        REFERENCES tb_livros(id_livro) ON DELETE CASCADE
);

-- 12. EMPRESTIMO
CREATE TABLE tb_emprestimo (
    id_emprestimo INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    data_emprestimo DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    data_prevista_devolucao DATE,
    data_devolucao DATE,
    CONSTRAINT fk_tb_emprestimo_usuario FOREIGN KEY (id_usuario)
        REFERENCES tb_usuario(id_usuario) ON DELETE NO ACTION
);

-- 13. ITEM_EMPRESTIMO
CREATE TABLE tb_item_emprestimo (
    id_item_emprestimo INT IDENTITY(1,1) PRIMARY KEY,
    id_emprestimo INT NOT NULL,
    id_exemplar INT NOT NULL,
    CONSTRAINT fk_tb_itememprestimo_emprestimo FOREIGN KEY (id_emprestimo)
        REFERENCES tb_emprestimo(id_emprestimo) ON DELETE CASCADE,
    CONSTRAINT fk_tb_itememprestimo_exemplar FOREIGN KEY (id_exemplar)
        REFERENCES tb_exemplares(id_exemplar) ON DELETE NO ACTION
);

-- 14. LOG SISTEMA
CREATE TABLE tb_log_sistema (
    id_log INT IDENTITY(1,1) PRIMARY KEY,
    id_aluno DECIMAL(10, 0),
    descricao VARCHAR(120),
    data_registro DATETIME DEFAULT GETDATE()
);
GO

-- ============================================
-- STORED PROCEDURE
-- ============================================

CREATE PROCEDURE sp_reg_log_sistema
    @p_id_usuario DECIMAL(10, 0),
    @p_evento VARCHAR(120)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO tb_log_sistema (id_aluno, descricao)
    VALUES (@p_id_usuario, @p_evento);
END;
GO;
