  # Sistema Integral de Gestión Operativa Web - Plataforma Completa de Turismo y E-commerce

## Resumen

Este repositorio integra un sistema completo multi-tenant para turismo con capacidades de e-commerce, gestión de reservaciones, y personalización total mediante paneles administrativos. El sistema está diseñado para ser altamente configurable y escalable.

---

## FUNCIONALIDADES DEL LADO DEL CLIENTE

### Sistema de Páginas Dinámicas
- **Páginas principales:** Home, Nosotros, Servicios, Productos, Galería, Contacto
- **Contenido 100% personalizable** desde el panel de desarrollo
- **Secciones modulares** que se pueden agregar, editar y reordenar
- **Footer dinámico** con mapa, galería y copyright personalizable

### Tipos de Secciones Disponibles
1. **Hero/Banner** - Banner principal con imagen de fondo y overlay
2. **Carousel** - Carrusel de imágenes con navegación
3. **Texto con imágenes** - Bloques de texto con 1-2 imágenes
4. **Features/Características** - Tarjetas de beneficios o características
5. **Testimonios** - Sistema de reseñas y testimonios
6. **Call to Action (CTA)** - Botones de acción personalizables
7. **Galería de imágenes** - Grid de fotos con lightbox
8. **Mapa de Google** - Integración de mapas con dirección
9. **Formulario de contacto** - Formularios personalizables
10. **Instagram Feed** - Galería de redes sociales
11. **Accordion de Servicios** - Tarjetas expandibles de servicios

### Sistema de Temas
- **Personalización completa de colores:**
  - Color primario
  - Color secundario
  - Color de acento
  - Color de texto
  - Color de fondo
- **Tipografía personalizable:**
  - Fuente principal
  - Fuente secundaria
- **Estilos de navbar:**
  - Transparente con scroll
  - Negro sólido
  - Color primario
- **Logo personalizable** para header y footer

### Sistema de E-commerce

#### Catálogo de Productos
- **Vista de grid responsiva** con filtros por categoría
- **Búsqueda de productos** en tiempo real
- **Paginación** (12 productos por página)
- **Imágenes de producto** con placeholder automático
- **Atributos personalizados** configurables por empresa
- **Categorías personalizadas** con descripciones
- **Productos perecederos** con fecha de caducidad
- **Control de stock** con badges de disponibilidad
- **SKU y gestión de inventario**

#### Detalle de Producto
- **Galería de imágenes** (imagen principal + relacionadas)
- **Información completa:** descripción, precio, stock, SKU
- **Atributos personalizados** dinámicos
- **Productos relacionados** por categoría
- **Sistema de reseñas** integrado (opcional)
- **Selector de cantidad** con validación de stock

#### Carrito de Compras
- **Gestión en sesión** (sin necesidad de login)
- **Actualización dinámica** de cantidades
- **Cálculo automático** de subtotales y total
- **Persistencia** entre páginas
- **Contador en navbar** con badge visual
- **Botones de incremento/decremento** inline

#### Proceso de Checkout
- **Formulario de datos del cliente:**
  - Nombre completo
  - Email
  - Teléfono
  - Dirección de entrega
  - Notas adicionales
- **Métodos de pago:**
  - Efectivo (contra entrega)
  - Transferencia bancaria
  - Tarjeta en tienda física
- **Resumen del pedido** con desglose
- **Validación de formularios** en frontend y backend

#### Confirmación de Pedido
- **Número de pedido único** generado automáticamente
- **Resumen completo** con todos los detalles
- **Estado del pedido** visible
- **Información de contacto** de la empresa
- **Próximos pasos** detallados según método de pago

### Sistema de Reservaciones

#### Tipos de Servicios
- **Servicios turísticos:** Avistamiento, Agroturismo, Gastroturismo, etc.
- **Hospedaje:** Cabañas, Camping, Glamping
- **Experiencias:** Tours, Talleres, Eventos especiales

#### Funcionalidades de Reservación
- **Calendario de disponibilidad** integrado
- **Selector de fechas** (check-in/check-out)
- **Cantidad de personas** (adultos, niños, bebés)
- **Precios dinámicos** por tipo de servicio
- **Servicios adicionales** opcionales
- **Notas especiales** del cliente
- **Confirmación por email** con SMTP configurable

### Sistema de Contacto

#### Formulario Personalizable
- **Campos dinámicos** configurables desde admin:
  - Mensaje (textarea)
  - Nombre (texto)
  - Email (validado)
  - Asunto
  - Teléfono (opcional)
  - Cualquier campo personalizado
- **Validación en tiempo real**
- **Protección CSRF**
- **Placeholders personalizables**
- **Botón con colores configurables**

#### Gestión de Mensajes
- **Almacenamiento en BD** de todos los mensajes
- **Campos capturados:**
  - Datos del formulario (JSON flexible)
  - Fecha y hora de envío
  - IP del remitente
  - User Agent
  - Estado: leído/no leído
  - Estado: respondido/pendiente
  - Notas internas del staff
- **Envío automático por email** vía SMTP
- **Notificación al correo de la empresa**

### Sistema de Reseñas
- **Reseñas para productos y servicios**
- **Calificación de 1-5 estrellas**
- **Comentarios de texto**
- **Sistema de aprobación** por administrador
- **Cálculo automático** de promedio de calificaciones
- **Vista de usuario** con sus propias reseñas
- **Restricción:** una reseña por usuario por producto/servicio

### Sistema de Autenticación
- **Registro de usuarios** con validación
- **Login/Logout** con sesiones seguras
- **Perfil de usuario** editable
- **Roles dinámicos** configurables:
  - Administrador
  - Empleado
  - Encargado
  - Cliente
  - Roles personalizados con atributos

### Características Responsivas
- **Diseño mobile-first**
- **Navbar responsive** con menú hamburguesa
- **Grid adaptativo** para productos y servicios
- **Imágenes optimizadas** con lazy loading
- **Touch-friendly** para dispositivos móviles

---

## PANEL ADMINISTRATIVO (AdminPanel)

### Dashboard
- **Vista general** de ventas y pedidos
- **Estadísticas en tiempo real:**
  - Ventas del día/semana/mes
  - Pedidos pendientes
  - Productos más vendidos
  - Reservaciones próximas
- **Gráficos visuales** de rendimiento
- **Accesos rápidos** a secciones principales

### Gestión de Productos

#### CRUD Completo
- **Crear productos** con formulario completo
- **Editar productos** existentes
- **Eliminar productos** (soft delete recomendado)
- **Listar productos** con filtros y búsqueda

#### Campos de Producto
- Nombre
- Descripción
- Precio
- Stock
- SKU (generado automáticamente)
- Categoría
- Imagen principal
- Perecedero (Sí/No)
- Fecha de caducidad (si es perecedero)
- Atributos personalizados (JSON)
- Estado: Activo/Inactivo

#### Categorías de Productos
- **Crear categorías** con nombre y descripción
- **Asignar empresas** específicas
- **Organización jerárquica**

### Gestión de Pedidos

#### Vista de Pedidos
- **Listado completo** con filtros por:
  - Estado (Pendiente, Confirmado, En camino, Entregado, Cancelado)
  - Fecha
  - Método de pago
  - Cliente
- **Búsqueda** por número de pedido o cliente
- **Ordenamiento** personalizable

#### Detalle de Pedido
- **Información del cliente:**
  - Nombre, email, teléfono
  - Dirección de entrega
  - Notas especiales
- **Productos del pedido:**
  - Lista completa con cantidades
  - Precios unitarios
  - Subtotales
- **Gestión de estado:**
  - Actualizar estado del pedido
  - Agregar notas internas
  - Historial de cambios
- **Total del pedido** y método de pago

#### Reportes de Ventas
- **Exportar a PDF** con filtros
- **Estadísticas de ventas** por periodo
- **Productos más vendidos**
- **Análisis de ingresos**

### Gestión de Reservaciones

#### Vista de Reservaciones
- **Calendario visual** de reservaciones
- **Listado** con filtros por:
  - Fecha
  - Servicio
  - Estado (Pendiente, Confirmada, Completada, Cancelada)
  - Cliente
- **Búsqueda avanzada**

#### Detalle de Reservación
- **Información del cliente**
- **Detalles del servicio reservado**
- **Fechas:** check-in, check-out, duración
- **Cantidad de personas:** adultos, niños, bebés
- **Servicios adicionales** incluidos
- **Total y método de pago**
- **Cambiar estado** de la reservación
- **Notas del cliente y del staff**

### Gestión de Novedades
- **Crear anuncios** para la página principal
- **Título, descripción, imagen**
- **Fecha de publicación**
- **Estado:** Publicado/Borrador
- **Orden de aparición**

### Gestión de Mensajes de Contacto
- **Bandeja de entrada** con todos los mensajes
- **Filtros:**
  - Leído/No leído
  - Respondido/Pendiente
  - Por fecha
- **Ver detalles completos:**
  - Todos los campos del formulario
  - IP y User Agent
  - Fecha de envío
- **Marcar como leído/respondido**
- **Agregar notas internas**
- **Responder directamente** (si SMTP configurado)

### Gestión de Reseñas
- **Moderar reseñas** pendientes
- **Aprobar/Rechazar** reseñas
- **Ver calificaciones** por producto/servicio
- **Responder a reseñas** (opcional)
- **Eliminar reseñas** inapropiadas

### Gestión de Usuarios

#### CRUD de Usuarios
- **Ver todos los usuarios** registrados
- **Crear usuarios** manualmente
- **Editar información:**
  - Nombre, email, teléfono
  - Rol asignado
  - Estado: Activo/Inactivo
- **Eliminar usuarios**
- **Resetear contraseñas**

#### Roles y Permisos
- **Asignar roles** dinámicos
- **Atributos personalizados** por rol
- **Gestión de permisos** granular

### Configuración de Empresa

#### Información Básica
- Nombre de la empresa
- Descripción
- Logo
- Información de contacto:
  - Teléfono
  - Email de contacto
  - Dirección física
  - Redes sociales

#### Configuración SMTP
- **Host SMTP** (ej: smtp.gmail.com)
- **Puerto** (587, 465, etc.)
- **Usuario SMTP**
- **Contraseña/Token**
- **Use TLS/SSL**
- **Email de envío**
- **Email de destino** para notificaciones


### Reportes y Analytics
- **Ventas por periodo**
- **Productos más vendidos**
- **Servicios más reservados**
- **Análisis de clientes**
- **Exportación a PDF/Excel**

---

## PANEL DE DESARROLLO (DevPanel)

### Gestión Multi-Empresa
- **Crear nuevas empresas** en el sistema
- **Activar/Desactivar** empresas
- **Cambiar empresa activa** para edición
- **Configuración independiente** por empresa
- **Isolación de datos** entre empresas

### Editor de Temas

#### Personalización Visual
- **Colores del sitio:**
  - Color primario (botones, enlaces principales)
  - Color secundario (hover, backgrounds)
  - Color de acento (CTAs, highlights)
  - Color de texto
  - Color de fondo
- **Tipografía:**
  - Fuente principal (body)
  - Fuente secundaria (headings)
  - Tamaños y pesos personalizables
- **Logos:**
  - Logo para header
  - Logo para footer
  - Favicon

#### Estilos de Navbar
- **Transparente con scroll:** Inicia transparente, se vuelve sólida al scrollear
- **Negro sólido:** Navbar negra siempre visible
- **Color primario:** Usa el color principal del tema

### Editor de Páginas y Secciones

#### Gestión de Páginas
- **Páginas disponibles:**
  - Home (Inicio)
  - Nosotros (About)
  - Servicios (Services)
  - Productos (Products)
  - Galería (Gallery)
  - Contacto (Contact)
  - Footer
- **Activar/Desactivar** páginas
- **Personalizar título** de cada página

#### Gestión de Secciones
- **Crear secciones nuevas** para cualquier página
- **Tipos de sección disponibles:**
  1. **Hero/Banner:** Banner con imagen de fondo, título, subtítulo
  2. **Carousel:** Carrusel de imágenes con descripciones
  3. **Texto con imágenes:** 1 o 2 imágenes con contenido de texto
  4. **Features:** Tarjetas de características con iconos
  5. **Testimonios:** Reseñas de clientes con fotos
  6. **CTA:** Botones de llamado a la acción
  7. **Galería:** Grid de imágenes con lightbox
  8. **Mapa:** Google Maps embebido
  9. **Instagram Feed:** Galería de redes sociales
  10. **Formulario de contacto:** Formulario personalizable
  11. **Accordion de servicios:** Tarjetas de servicios

#### Editor de Configuración JSON
- **Editor visual** para cada tipo de sección
- **Configuración en JSON** con validación
- **Campos dinámicos** según tipo de sección
- **Preview en tiempo real** (opcional)

#### Ejemplos de Configuración por Tipo:

**Hero:**
```json
{
  "titulo": "Bienvenido a Xoletongo",
  "subtitulo": "Turismo Natural Sostenible",
  "bg_class": "breadcam_bg_tienda",
  "bg_image": "img/banner/banner.png",
  "opacidad": 0.4
}
```

**Formulario de Contacto:**
```json
{
  "titulo": "Contáctanos",
  "texto_boton": "Enviar Mensaje",
  "boton_bg_color": "#2d6a2e",
  "boton_text_color": "#ffffff",
  "boton_hover_color": "#4caf50",
  "campos": [
    {
      "nombre": "mensaje",
      "tipo": "textarea",
      "placeholder": "Tu mensaje",
      "requerido": true,
      "filas": 9
    },
    {
      "nombre": "nombre",
      "tipo": "text",
      "placeholder": "Tu nombre",
      "requerido": true,
      "columnas": 6
    }
  ],
  "info_contacto": [
    {
      "icono": "ti-home",
      "titulo": "Dirección",
      "subtitulo": "Ciudad, Estado"
    }
  ]
}
```

**Texto con Imágenes:**
```json
{
  "titulo": "Nuestra Historia",
  "contenido": "Descripción detallada...",
  "layout": "imagen_izquierda",
  "imagen_1": "img/about/about_1.png",
  "imagen_2": "img/about/about_2.png",
  "span_titulo": "Sobre Nosotros",
  "boton_texto": "Leer más",
  "boton_url": "/nosotros"
}
```

#### Gestión de Orden
- **Arrastrar y soltar** para reordenar (planeado)
- **Botones de subir/bajar** orden
- **Número de orden manual**
- **Vista previa** del orden en la página

#### Toggle de Activación
- **Activar/Desactivar** secciones sin eliminarlas
- **Útil para:** pruebas, temporadas, A/B testing

### Atributos Personalizados

#### Para Productos
- **Crear atributos** específicos del negocio:
  - Talla (texto)
  - Color (texto)
  - Material (texto)
  - Peso (número)
  - Caducidad (fecha)
  - Orgánico (checkbox)
- **Tipos de dato:** Texto, Textarea, Número, Fecha, Boolean
- **Aplicar a productos** de forma flexible

#### Para Servicios
- **Atributos de servicios:**
  - Duración
  - Nivel de dificultad
  - Incluye comida
  - Guía incluido
  - Equipo necesario
- **Personalización por tipo** de servicio

### Sistema de Roles Dinámicos

#### Crear Roles Personalizados
- **Nombre del rol** (ej: "Guía Turístico")
- **Descripción** de responsabilidades
- **Empresa específica**
- **Estado:** Activo/Inactivo

#### Atributos de Rol (Schema)
- **Definir campos** específicos del rol:
  - Turno (lista: Matutino, Vespertino)
  - Especialidad (texto)
  - Certificación (fecha)
  - Idiomas (lista múltiple)
- **Tipos de campo:**
  - Texto corto
  - Texto largo
  - Número
  - Fecha
  - Lista de opciones
  - Lista múltiple
  - Checkbox
- **Campos requeridos** u opcionales

#### Asignar Roles a Usuarios
- **Desde el panel de usuarios**
- **Llenar atributos** personalizados
- **Validación automática** de campos requeridos

### Comandos de Gestión (Management Commands)

#### Seeders Disponibles
- `seed_xoletongo_content` - Contenido inicial de Home
- `seed_nosotros_content` - Página de Nosotros
- `seed_servicios_content` - Página de Servicios
- `seed_contacto_content` - Página de Contacto
- `seed_galeria_content` - Página de Galería
- `crear_pagina_footer` - Footer del sitio
- `crear_pagina_productos` - Página de Productos

#### Utilidades
- `migrar_roles_legacy` - Migrar roles antiguos al nuevo sistema
- `actualizar_tema_xoletongo` - Actualizar tema de la empresa
- `actualizar_color_boton_contacto` - Personalizar botón de contacto

### Gestión de Superusuarios
- **Crear superusuarios** desde el devpanel
- **Editar información** de administradores
- **Asignar permisos** especiales
- **Activar/Desactivar** cuentas de admin

---

## MEJORAS TÉCNICAS Y ARQUITECTURA

### Arquitectura Multi-Tenant
- **Isolación de datos** por empresa
- **Configuración independiente** por tenant
- **Escalabilidad horizontal**
- **Cambio dinámico** de empresa activa en sesión

### Sistema de Temas Dinámicos
- **CSS Variables** para personalización en tiempo real
- **Colores configurables** sin recompilar
- **Fuentes personalizadas** con Google Fonts
- **Responsive design** automático

### Base de Datos
- **Modelos relacionales** bien estructurados
- **JSON Fields** para configuraciones flexibles
- **Índices optimizados** para búsquedas
- **Migraciones versionadas** con Django

### Sistema de Email
- **Backend SMTP personalizado** por empresa
- **Configuración dinámica** sin reiniciar
- **Soporte para Gmail, Outlook, SendGrid, etc.**
- **Templates personalizables**
- **Cola de emails** (recomendado para producción)

### Seguridad
- **CSRF Protection** en todos los formularios
- **SQL Injection prevention** con ORM
- **XSS Protection** con escapado automático
- **Autenticación basada en sesiones**
- **Middleware de seguridad** Django
- **Validación de permisos** en vistas sensibles

### Frontend Responsivo
- **Bootstrap 4/5** como base
- **CSS Grid y Flexbox** para layouts
- **Media queries** optimizadas
- **Touch-friendly** para móviles
- **Progressive enhancement**

### Optimizaciones
- **Lazy loading** de imágenes
- **Static files** optimizados
- **Database queries** optimizadas con `select_related`
- **Paginación** para listados largos
- **Caché** de configuraciones (recomendado)

### Testing (Recomendado)
- Tests unitarios para modelos
- Tests de integración para vistas
- Tests de formularios
- Tests de APIs (si se implementan)

---

## TECNOLOGÍAS UTILIZADAS

### Backend
- **Django 5.2** - Framework web
- **Python 3.13** - Lenguaje de programación
- **MySQL** - Base de datos
- **PyMySQL** - Conector de base de datos

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos
- **JavaScript/jQuery** - Interactividad
- **Bootstrap** - Framework CSS
- **Font Awesome** - Iconos
- **Themify Icons** - Iconos adicionales
- **Owl Carousel** - Carruseles
- **Magnific Popup** - Lightbox

### Librerías Python
- **Pillow** - Procesamiento de imágenes
- **ReportLab** - Generación de PDFs
- **django-widget-tweaks** - Personalización de formularios
- **PayPal REST SDK** - Integración de pagos (preparado)

---

## INSTALACIÓN Y CONFIGURACIÓN

### Requisitos Previos
- Python 3.13+
- MySQL 5.7+ o MariaDB
- pip y virtualenv

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone [url-del-repositorio]
cd Xoletongo
```

2. **Crear entorno virtual**
```bash
python -m venv mienv
# Windows:
mienv\Scripts\activate
# Linux/Mac:
source mienv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
- Crear base de datos MySQL:
```sql
CREATE DATABASE xoletongo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'userD'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON xoletongo.* TO 'userD'@'localhost';
FLUSH PRIVILEGES;
```

- Editar `settings.py` con tus credenciales si es necesario

5. **Ejecutar migraciones**
```bash
cd xoletongo
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Crear empresa inicial**
```bash
python manage.py shell
>>> from empresas.models import Empresa
>>> empresa = Empresa.objects.create(
...     nombre='Tu Empresa',
...     activa=True
... )
>>> exit()
```

8. **Cargar contenido inicial (opcional)**
```bash
python manage.py seed_xoletongo_content
python manage.py seed_nosotros_content
python manage.py seed_servicios_content
python manage.py seed_contacto_content
python manage.py seed_galeria_content
python manage.py crear_pagina_footer
python manage.py crear_pagina_productos
```

9. **Recolectar archivos estáticos (producción)**
```bash
python manage.py collectstatic
```

10. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

### Acceder al Sistema
- **Sitio público:** http://localhost:8000
- **Panel Admin:** http://localhost:8000/admin/
- **Dev Panel:** http://localhost:8000/dev/

**Nota:** El proyecto usa "Xoletongo" como empresa de ejemplo/demo en la base de datos.

---

## CONFIGURACIÓN POST-INSTALACIÓN

### 1. Configurar Empresa
Desde el AdminPanel o DevPanel:
- Subir logo
- Agregar información de contacto
- Configurar SMTP para emails
- Habilitar módulos necesarios (Productos, Servicios, Reseñas)

### 2. Configurar Tema
Desde el DevPanel:
- Elegir colores corporativos
- Seleccionar fuentes
- Configurar estilo de navbar
- Subir logos personalizados

### 3. Personalizar Páginas
Desde el DevPanel → Secciones:
- Editar Home con hero, features, testimonios
- Configurar página de Nosotros
- Personalizar Contacto con tu mapa
- Configurar Footer

### 4. Agregar Productos/Servicios
Desde el AdminPanel:
- Crear categorías
- Agregar productos con imágenes
- Configurar servicios turísticos
- Establecer precios

### 5. Configurar SMTP (para emails)
Desde AdminPanel → Configuración de Empresa:
- SMTP Host: smtp.gmail.com (ejemplo)
- Puerto: 587
- Usuario: tu-email@gmail.com
- Contraseña: contraseña de aplicación
- Use TLS: Activado

---

## NOTAS IMPORTANTES

### Para Desarrolladores
- **Siempre crear rama** antes de nuevas features
- **Ejecutar migraciones** después de cambios en modelos
- **Consultar antes de migrar** cambios importantes
- **Documentar cambios** en el código
- **Testing recomendado** antes de merge

### Para Administradores
- **Backup regular** de la base de datos
- **Actualizar configuración SMTP** para emails
- **Revisar logs** periódicamente
- **Monitorear espacio** de media files
- **Activar SSL** en producción

### Limitaciones Conocidas
- Sistema de pagos PayPal preparado pero requiere configuración
- Caché no implementado (recomendado para producción)
- Tests unitarios pendientes
- API REST no implementada (extensión futura)

---

## ROADMAP FUTURO (Sugerencias)

### Corto Plazo
- [x] Implementar sistema de caché
- [ ] Agregar tests unitarios
- [x] Optimizar queries de base de datos
- [ ] Mejorar SEO (meta tags, sitemap)
- [x] Implementar búsqueda avanzada

### Mediano Plazo
- [ ] API REST para mobile app
- [ ] Sistema de notificaciones push
- [x] Integración completa de PayPal
- [x] Sistema de cupones/descuentos
- [x] Dashboard analytics mejorado

### Largo Plazo
- [x] App móvil nativa
- [x] Integración con redes sociales
- [ ] Sistema de lealtad/puntos
- [ ] Marketplace multi-vendor
- [ ] IA para recomendaciones


---

## LICENCIA

MIT License

Copyright © 2025 [Carlos Hernandez & Danitza Ramos] - Proyecto de Residencias Profesionales Académico

Desarrollado como parte del plan de del Banco de Proyectos 2025
Tecnológico Nacional de México - Instituto Tecnológico de Apizaco

---

## AUTORES

- **Equipo de Desarrollo del Sistema Integral de Gestión Operativa Web**
- Carlos Alberto Hernández Sastré - Software Developer 
- Danitza Anhel Ramos Chavez - Software Developer
- Ing. Juan Ramos Ramos - Asesor del Proyecto

---

## SOPORTE

Para soporte técnico o preguntas:
- Email: L20370955@apizaco.tecnm.mx

---

**¡Gracias por usar el Sistema Integral de Gestión Operativa Web!**

