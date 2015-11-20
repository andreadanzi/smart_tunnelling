-- phpMyAdmin SQL Dump
-- version 4.2.7.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 20, 2015 alle 07:42
-- Versione del server: 5.5.39
-- PHP Version: 5.4.31

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `bbtsws`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `bbtgeoitem`
--

CREATE TABLE IF NOT EXISTS `bbtgeoitem` (
`keyp` int(11) NOT NULL,
  `inizio` decimal(15,5) DEFAULT NULL,
  `fine` decimal(15,5) DEFAULT NULL,
  `l` decimal(15,5) DEFAULT NULL,
  `perc` decimal(15,5) DEFAULT NULL,
  `type` varchar(128) DEFAULT NULL,
  `g_med` decimal(15,5) DEFAULT NULL,
  `g_stddev` decimal(15,5) DEFAULT NULL,
  `sigma_ci_avg` decimal(15,5) DEFAULT NULL,
  `sigma_ci_stdev` decimal(15,5) DEFAULT NULL,
  `mi_med` decimal(15,5) DEFAULT NULL,
  `mi_stdev` decimal(15,5) DEFAULT NULL,
  `ei_med` decimal(15,5) DEFAULT NULL,
  `ei_stdev` decimal(15,5) DEFAULT NULL,
  `cai_med` decimal(15,5) DEFAULT NULL,
  `cai_stdev` decimal(15,5) DEFAULT NULL,
  `gsi_med` decimal(15,5) DEFAULT NULL,
  `gsi_stdev` varchar(128) DEFAULT NULL,
  `id` int(11) DEFAULT NULL,
  `rmr_med` decimal(15,5) DEFAULT NULL,
  `rmr_stdev` decimal(15,5) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `sigma_ti_min` decimal(15,5) DEFAULT NULL,
  `sigma_ti_max` decimal(15,5) DEFAULT NULL,
  `k0_min` decimal(15,5) DEFAULT NULL,
  `k0_max` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbtparameter`
--

CREATE TABLE IF NOT EXISTS `bbtparameter` (
`keyp` int(11) NOT NULL,
  `inizio` decimal(15,5) DEFAULT NULL,
  `fine` decimal(15,5) DEFAULT NULL,
  `est` decimal(15,5) DEFAULT NULL,
  `nord` decimal(15,5) DEFAULT NULL,
  `he` decimal(15,5) DEFAULT NULL,
  `hp` decimal(15,5) DEFAULT NULL,
  `co` decimal(15,5) DEFAULT NULL,
  `tipo` varchar(128) DEFAULT NULL,
  `g_med` decimal(15,5) DEFAULT NULL,
  `g_stddev` decimal(15,5) DEFAULT NULL,
  `sigma_ci_avg` decimal(15,5) DEFAULT NULL,
  `sigma_ci_stdev` decimal(15,5) DEFAULT NULL,
  `mi_med` decimal(15,5) DEFAULT NULL,
  `mi_stdev` decimal(15,5) DEFAULT NULL,
  `ei_med` decimal(15,5) DEFAULT NULL,
  `ei_stdev` decimal(15,5) DEFAULT NULL,
  `cai_med` decimal(15,5) DEFAULT NULL,
  `cai_stdev` decimal(15,5) DEFAULT NULL,
  `gsi_med` decimal(15,5) DEFAULT NULL,
  `gsi_stdev` decimal(15,5) DEFAULT NULL,
  `profilo_id` int(11) DEFAULT NULL,
  `geoitem_id` int(11) DEFAULT NULL,
  `rmr_med` decimal(15,5) DEFAULT NULL,
  `rmr_stdev` decimal(15,5) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `sigma_ti_min` decimal(15,5) DEFAULT NULL,
  `sigma_ti_max` decimal(15,5) DEFAULT NULL,
  `k0_min` decimal(15,5) DEFAULT NULL,
  `k0_max` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbtparametereval`
--

CREATE TABLE IF NOT EXISTS `bbtparametereval` (
`keyp` int(11) NOT NULL,
  `insertdate` varchar(128) DEFAULT NULL,
  `iteration_no` int(11) DEFAULT NULL,
  `fine` decimal(15,5) DEFAULT NULL,
  `he` decimal(15,5) DEFAULT NULL,
  `hp` decimal(15,5) DEFAULT NULL,
  `co` decimal(15,5) DEFAULT NULL,
  `gamma` decimal(15,5) DEFAULT NULL,
  `sigma` decimal(15,5) DEFAULT NULL,
  `mi` decimal(15,5) DEFAULT NULL,
  `ei` decimal(15,5) DEFAULT NULL,
  `cai` decimal(15,5) DEFAULT NULL,
  `gsi` decimal(15,5) DEFAULT NULL,
  `rmr` decimal(15,5) DEFAULT NULL,
  `pkgl` decimal(15,5) DEFAULT NULL,
  `closure` decimal(15,5) DEFAULT NULL,
  `rockburst` decimal(15,5) DEFAULT NULL,
  `front_stability_ns` decimal(15,5) DEFAULT NULL,
  `front_stability_lambda` decimal(15,5) DEFAULT NULL,
  `penetrationRate` decimal(15,5) DEFAULT NULL,
  `penetrationRateReduction` decimal(15,5) DEFAULT NULL,
  `contactThrust` decimal(15,5) DEFAULT NULL,
  `torque` decimal(15,5) DEFAULT NULL,
  `frictionForce` decimal(15,5) DEFAULT NULL,
  `requiredThrustForce` decimal(15,5) DEFAULT NULL,
  `availableThrust` decimal(15,5) DEFAULT NULL,
  `dailyAdvanceRate` decimal(15,5) DEFAULT NULL,
  `profilo_id` int(11) DEFAULT NULL,
  `geoitem_id` int(11) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `sigma_ti` decimal(15,5) DEFAULT NULL,
  `k0` decimal(15,5) DEFAULT NULL,
  `t0` decimal(15,5) DEFAULT NULL,
  `t1` decimal(15,5) DEFAULT NULL,
  `t3` decimal(15,5) DEFAULT NULL,
  `t4` decimal(15,5) DEFAULT NULL,
  `t5` decimal(15,5) DEFAULT NULL,
  `tunnelName` varchar(128) DEFAULT NULL,
  `tbmName` varchar(128) DEFAULT NULL,
  `inSituConditionSigmaV` decimal(15,5) DEFAULT NULL,
  `tunnelRadius` decimal(15,5) DEFAULT NULL,
  `rockE` decimal(15,5) DEFAULT NULL,
  `mohrCoulombPsi` decimal(15,5) DEFAULT NULL,
  `rockUcs` decimal(15,5) DEFAULT NULL,
  `inSituConditionGsi` decimal(15,5) DEFAULT NULL,
  `hoekBrownMi` decimal(15,5) DEFAULT NULL,
  `hoekBrownD` decimal(15,5) DEFAULT NULL,
  `hoekBrownMb` decimal(15,5) DEFAULT NULL,
  `hoekBrownS` decimal(15,5) DEFAULT NULL,
  `hoekBrownA` decimal(15,5) DEFAULT NULL,
  `hoekBrownMr` decimal(15,5) DEFAULT NULL,
  `hoekBrownSr` decimal(15,5) DEFAULT NULL,
  `hoekBrownAr` decimal(15,5) DEFAULT NULL,
  `urPiHB` decimal(15,5) DEFAULT NULL,
  `rpl` decimal(15,5) DEFAULT NULL,
  `picr` decimal(15,5) DEFAULT NULL,
  `ldpVlachBegin` decimal(15,5) DEFAULT NULL,
  `ldpVlachEnd` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbtprofilo`
--

CREATE TABLE IF NOT EXISTS `bbtprofilo` (
`keyp` int(11) NOT NULL,
  `inizio` decimal(15,5) DEFAULT NULL,
  `fine` decimal(15,5) DEFAULT NULL,
  `est` decimal(15,5) DEFAULT NULL,
  `nord` decimal(15,5) DEFAULT NULL,
  `he` decimal(15,5) DEFAULT NULL,
  `hp` decimal(15,5) DEFAULT NULL,
  `co` decimal(15,5) DEFAULT NULL,
  `tipo` varchar(128) DEFAULT NULL,
  `id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbtreliability`
--

CREATE TABLE IF NOT EXISTS `bbtreliability` (
`keyp` int(11) NOT NULL,
  `id` int(11) DEFAULT NULL,
  `inizio` decimal(15,5) DEFAULT NULL,
  `fine` decimal(15,5) DEFAULT NULL,
  `gmr_class` decimal(15,5) DEFAULT NULL,
  `gmr_val` decimal(15,5) DEFAULT NULL,
  `reliability` decimal(15,5) DEFAULT NULL,
  `eval_var` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbttbm`
--

CREATE TABLE IF NOT EXISTS `bbttbm` (
  `name` varchar(128) NOT NULL,
  `alignmentCode` varchar(128) DEFAULT NULL,
  `manufacturer` varchar(128) DEFAULT NULL,
  `type` varchar(128) DEFAULT NULL,
  `shieldLength` decimal(15,5) DEFAULT NULL,
  `overcut` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `bbttbmkpi`
--

CREATE TABLE IF NOT EXISTS `bbttbmkpi` (
  `tunnelName` varchar(128) DEFAULT NULL,
  `tbmName` varchar(128) DEFAULT NULL,
  `iterationNo` int(11) DEFAULT NULL,
  `kpiKey` decimal(15,5) DEFAULT NULL,
  `kpiDescr` decimal(15,5) DEFAULT NULL,
  `minImpact` decimal(15,5) DEFAULT NULL,
  `maxImpact` decimal(15,5) DEFAULT NULL,
  `avgImpact` decimal(15,5) DEFAULT NULL,
  `appliedLength` decimal(15,5) DEFAULT NULL,
  `percentOfApplication` decimal(15,5) DEFAULT NULL,
  `probabilityScore` decimal(15,5) DEFAULT NULL,
  `totalImpact` decimal(15,5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bbtgeoitem`
--
ALTER TABLE `bbtgeoitem`
 ADD PRIMARY KEY (`keyp`);

--
-- Indexes for table `bbtparameter`
--
ALTER TABLE `bbtparameter`
 ADD PRIMARY KEY (`keyp`);

--
-- Indexes for table `bbtparametereval`
--
ALTER TABLE `bbtparametereval`
 ADD PRIMARY KEY (`keyp`);

--
-- Indexes for table `bbtprofilo`
--
ALTER TABLE `bbtprofilo`
 ADD PRIMARY KEY (`keyp`);

--
-- Indexes for table `bbtreliability`
--
ALTER TABLE `bbtreliability`
 ADD PRIMARY KEY (`keyp`);

--
-- Indexes for table `bbttbm`
--
ALTER TABLE `bbttbm`
 ADD PRIMARY KEY (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bbtgeoitem`
--
ALTER TABLE `bbtgeoitem`
MODIFY `keyp` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `bbtparameter`
--
ALTER TABLE `bbtparameter`
MODIFY `keyp` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `bbtparametereval`
--
ALTER TABLE `bbtparametereval`
MODIFY `keyp` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `bbtprofilo`
--
ALTER TABLE `bbtprofilo`
MODIFY `keyp` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `bbtreliability`
--
ALTER TABLE `bbtreliability`
MODIFY `keyp` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
