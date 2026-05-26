# README: App de Reservas - Sistemas Distribuidos

Este repositorio contiene la configuración, automatización y despliegue de la **App de Reservas**, un proyecto basado en una arquitectura distribuida sobre contenedores Incus desplegados en Google Cloud Platform.

## Autores

- Santiago Potes Giraldo
- Cristian Camilo Vélez

---

# Descripción General

La plataforma permite gestionar reservas mediante una aplicación web distribuida y desplegada sobre infraestructura virtualizada.

La solución implementa:

- Virtualización ligera mediante Incus
- Segmentación de red privada
- Persistencia de datos
- Observabilidad y monitoreo
- Automatización mediante Infraestructura como Código (IaC)

---

# Arquitectura del Sistema

La aplicación utiliza una arquitectura distribuida donde cada servicio se ejecuta en un contenedor independiente.

La comunicación interna entre contenedores se realiza mediante una red privada administrada por Incus sobre la subred:

```
10.10.0.0/24
``` 

Inicialmente se contempló el uso de OVN/Open vSwitch; sin embargo, debido a limitaciones del entorno de virtualización, se implementó una red bridge administrada directamente por Incus manteniendo el aislamiento lógico entre servicios.

---

# Topología de Nodos

| Nodo         | IP         | Función Principal                            |
| ------------ | ---------- | -------------------------------------------- |
| webbox       | 10.10.0.2  | Reverse proxy y exposición externa           |
| node-control | 10.10.0.5  | Nodo centralizado de automatización e IaC    |
| app-api      | 10.10.0.10 | Ejecución de la aplicación Flask y endpoints |
| app-core     | 10.10.0.11 | Procesamiento de lógica de negocio           |
| db-postgres  | 10.10.0.12 | Base de datos persistente                    |
| monitoring   | 10.10.0.20 | Observabilidad, Prometheus y Grafana         |

---

# Flujo de la Aplicación

1. El usuario accede desde el navegador web.
2. La solicitud es recibida por la aplicación Flask.
3. La lógica de negocio procesa la reserva.
4. PostgreSQL almacena la información.
5. Prometheus recolecta métricas del sistema.
6. Grafana visualiza métricas y dashboards.

---

# Persistencia de Datos

El sistema garantiza disponibilidad y almacenamiento persistente mediante dos capas:

## PostgreSQL

Actúa como el motor principal de almacenamiento de reservas del aplicativo.

## MicroCeph

Garantiza persistencia del almacenamiento simulando una arquitectura distribuida tipo Ceph.

La persistencia se implementa mediante:

* Storage pools de Incus
* Volúmenes desacoplados
* Persistencia independiente del ciclo de vida de contenedores

---

# Infraestructura como Código (IaC)

Toda la infraestructura fue diseñada para minimizar configuraciones manuales y centralizar el despliegue desde el nodo `node-control`.

---

# Aprovisionamiento con OpenTofu

La infraestructura base se define utilizando OpenTofu.

El archivo `main.tf` se encarga de:

* Crear contenedores Incus
* Definir recursos base
* Aprovisionar nodos Ubuntu
* Configurar la topología inicial

## Contenedores Aprovisionados

* node-control
* app-api
* app-core
* db-postgres
* monitoring

---

# Configuración con Ansible

Una vez desplegados los contenedores, Ansible automatiza la instalación y configuración de servicios.

## Playbooks Utilizados

### bootstrap.yml

Instala dependencias base:

* curl
* wget
* git
* htop
* net-tools
* python3
* docker

---

### postgres.yml

Configura PostgreSQL:

* instalación
* usuarios
* permisos
* inicialización de base de datos

---

### exporters.yml

Instala Node Exporter para métricas de infraestructura.

Puerto utilizado:

```text
9100
```

---

### monitoring.yml

Despliega:

* Prometheus
* Grafana Enterprise

---

# Observabilidad y Monitoreo

El monitoreo permite supervisar:

* CPU
* RAM
* Disco
* Red
* Uptime
* Métricas de aplicación

---

## Prometheus

Recolecta métricas cada 15 segundos mediante scraping.

Puerto:

```text
9090
```

---

## Grafana

Centraliza dashboards y visualización operativa.

Puerto:

```text
3000
```

---

## Node Exporter

Instalado en cada nodo para exponer métricas del sistema operativo.

Puerto:

```text
9100
```

---

# Exposición de Servicios

Debido a que los contenedores se encuentran en una red privada administrada por Incus, se utilizó `socat` en la VM principal para realizar port forwarding hacia:

* Aplicación Flask
* Grafana
* Prometheus

Esto permite exponer únicamente los servicios necesarios al exterior manteniendo aislamiento interno.

---

# Acceso a Servicios

| Servicio   | URL                    |
| ---------- | ---------------------- |
| Aplicación | http://IP_PUBLICA:5000 |
| Grafana    | http://IP_PUBLICA:3000 |
| Prometheus | http://IP_PUBLICA:9090 |

---

# Requisitos Previos

* Google Cloud Platform
* Ubuntu Server 22.04/24.04
* Incus
* OpenTofu
* Ansible
* Python 3
* PostgreSQL
* Acceso sudo/root

---

# Despliegue del Proyecto

## 1. Clonar repositorio

```bash
git clone <REPOSITORIO>
cd Incus-Proyecto
```

---

## 2. Inicializar OpenTofu

```bash
cd infra
tofu init
tofu apply
```

---

## 3. Ejecutar Playbooks

```bash
cd ../ansible

ansible-playbook bootstrap.yml
ansible-playbook postgres.yml
ansible-playbook exporters.yml
ansible-playbook monitoring.yml
```

---

# Consideraciones de Seguridad

* Segmentación lógica mediante red privada
* Servicios internos no expuestos directamente a Internet
* Exposición controlada mediante forwarding
* Persistencia desacoplada
* Separación de responsabilidades entre contenedores

---

# Tecnologías Utilizadas

* Google Cloud Platform
* Incus
* OpenTofu
* Ansible
* PostgreSQL
* MicroCeph
* Prometheus
* Grafana
* Python
* Flask
* Docker
* Linux Ubuntu

---

# Diagrama de Arquitectura

El proyecto incluye diagramas de topología y arquitectura desarrollados en PlantUML.

---

# Conclusiones

El proyecto permitió implementar una arquitectura distribuida funcional sobre Google Cloud Platform utilizando virtualización ligera con Incus.

Se integraron mecanismos de automatización, monitoreo, persistencia y segmentación de red, logrando una plataforma funcional para gestión de reservas con capacidades de observabilidad y persistencia desacoplada.

La solución demuestra conceptos asociados a:

* Infraestructura como Código
* Virtualización ligera
* Observabilidad
* Redes privadas
* Persistencia distribuida
* Automatización de despliegues

```
```

