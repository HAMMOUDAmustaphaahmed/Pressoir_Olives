-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mer. 12 nov. 2025 à 10:39
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `pressoir_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `chart`
--

CREATE TABLE `chart` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `table_name` varchar(100) NOT NULL,
  `x_column` varchar(100) NOT NULL,
  `y_column` varchar(100) NOT NULL,
  `chart_type` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `season_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `chart`
--

INSERT INTO `chart` (`id`, `name`, `table_name`, `x_column`, `y_column`, `chart_type`, `created_at`, `user_id`, `season_id`) VALUES
(7, 'prodution', 'production', 'date_depot', 'quantite', 'line', '2025-11-11 14:41:21', 1, 1),
(8, 'Machines', 'machines', 'date_installation', 'nom', 'bar', '2025-11-12 09:24:20', 1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `column_metadata`
--

CREATE TABLE `column_metadata` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `table_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `column_metadata`
--

INSERT INTO `column_metadata` (`id`, `name`, `display_name`, `type`, `table_id`) VALUES
(35, 'numero', 'Numéro', 'integer', 18),
(36, 'nom_prenom', 'Nom et Prénom', 'string', 18),
(37, 'date_depot', 'Date de dépôt', 'date', 18),
(38, 'quantite', 'Quantité (Kg)', 'float', 18),
(39, 'montant_paye', 'Montant payé', 'float', 18),
(40, 'montant_restant', 'Montant restant', 'float', 18),
(41, 'rendement', 'Rendement (L/kg)', 'float', 18),
(42, 'caisses_utilisees', 'Caisses utilisées', 'string', 18),
(43, 'nombre_bidons', 'Nombre de bidons', 'string', 18),
(44, 'nom', 'Nom', 'string', 19),
(45, 'date_installation', 'Date Installation', 'string', 19),
(46, 'societe', 'Societé', 'string', 19);

-- --------------------------------------------------------

--
-- Structure de la table `company_settings`
--

CREATE TABLE `company_settings` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `address` text NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `logo` varchar(300) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `company_settings`
--

INSERT INTO `company_settings` (`id`, `name`, `address`, `phone`, `email`, `logo`) VALUES
(1, 'Pressoir à olives Hussein Letaief', 'Menzel Ennour', '12345678', 'test@gmail.com', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `machines`
--

CREATE TABLE `machines` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `date_installation` varchar(255) DEFAULT NULL,
  `societe` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `machines`
--

INSERT INTO `machines` (`id`, `nom`, `date_installation`, `societe`) VALUES
(1, 'test', '29/01/1990', 'test'),
(2, 'machine2', '01/01/1990', 'X');

-- --------------------------------------------------------

--
-- Structure de la table `production`
--

CREATE TABLE `production` (
  `id` int(11) NOT NULL,
  `numero` int(11) DEFAULT NULL,
  `nom_prenom` varchar(255) DEFAULT NULL,
  `date_depot` date DEFAULT NULL,
  `quantite` float DEFAULT NULL,
  `montant_paye` float DEFAULT NULL,
  `montant_restant` float DEFAULT NULL,
  `rendement` float DEFAULT NULL,
  `caisses_utilisees` varchar(255) DEFAULT NULL,
  `nombre_bidons` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `production`
--

INSERT INTO `production` (`id`, `numero`, `nom_prenom`, `date_depot`, `quantite`, `montant_paye`, `montant_restant`, `rendement`, `caisses_utilisees`, `nombre_bidons`) VALUES
(1, 1, 'Mohamed Saleh', '2025-11-11', 520, 56, 14, 0, '201,202', '2(20),1(2)'),
(2, 2, 'Foulani Flen', '2025-11-12', 850, 80, 10, 0, '332,254', '1(20),1(1)');

-- --------------------------------------------------------

--
-- Structure de la table `season`
--

CREATE TABLE `season` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `season`
--

INSERT INTO `season` (`id`, `name`, `start_date`, `end_date`, `is_active`, `created_at`) VALUES
(1, '2025-2026', '2025-11-01', '2026-04-30', 1, '2025-11-12 09:14:06');

-- --------------------------------------------------------

--
-- Structure de la table `table_metadata`
--

CREATE TABLE `table_metadata` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `season_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `table_metadata`
--

INSERT INTO `table_metadata` (`id`, `name`, `display_name`, `season_id`, `created_at`) VALUES
(18, 'production', 'Production', 1, '2025-11-11 14:38:43'),
(19, 'machines', 'Machines', 1, '2025-11-12 09:23:09');

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(120) NOT NULL,
  `access_level` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`id`, `username`, `password_hash`, `access_level`, `is_active`, `created_at`) VALUES
(1, 'admin', 'pbkdf2:sha256:600000$DtJGmlWtfmrEu1M5$d314c5a19dd741edfbf297969fb8e5592cc457550433f32b99e23c395db81820', 'full', 1, '2025-11-11 10:34:45'),
(2, 'manager', 'pbkdf2:sha256:600000$MZ30otQCggJXHV86$7a8c934c64532055e20fa710e1f02a802d4c1d9f8229a16f46179a2ecf9e2637', 'read_write_edit', 1, '2025-11-11 10:35:21'),
(3, 'user', 'pbkdf2:sha256:600000$Bjnr598Is9LW5Em8$e102e6f1dbb5d56c904559dc2bd295987aab938e0d2763aaf3d4b0aa615fdb6c', 'read_only', 1, '2025-11-11 14:47:16');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `chart`
--
ALTER TABLE `chart`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `fk_chart_season` (`season_id`);

--
-- Index pour la table `column_metadata`
--
ALTER TABLE `column_metadata`
  ADD PRIMARY KEY (`id`),
  ADD KEY `table_id` (`table_id`);

--
-- Index pour la table `company_settings`
--
ALTER TABLE `company_settings`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `machines`
--
ALTER TABLE `machines`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `production`
--
ALTER TABLE `production`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `season`
--
ALTER TABLE `season`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Index pour la table `table_metadata`
--
ALTER TABLE `table_metadata`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_table_per_season` (`name`,`season_id`),
  ADD KEY `fk_table_season` (`season_id`);

--
-- Index pour la table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `chart`
--
ALTER TABLE `chart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `column_metadata`
--
ALTER TABLE `column_metadata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT pour la table `company_settings`
--
ALTER TABLE `company_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `machines`
--
ALTER TABLE `machines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `production`
--
ALTER TABLE `production`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `season`
--
ALTER TABLE `season`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `table_metadata`
--
ALTER TABLE `table_metadata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT pour la table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `chart`
--
ALTER TABLE `chart`
  ADD CONSTRAINT `chart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `fk_chart_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `column_metadata`
--
ALTER TABLE `column_metadata`
  ADD CONSTRAINT `column_metadata_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `table_metadata` (`id`);

--
-- Contraintes pour la table `table_metadata`
--
ALTER TABLE `table_metadata`
  ADD CONSTRAINT `fk_table_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
