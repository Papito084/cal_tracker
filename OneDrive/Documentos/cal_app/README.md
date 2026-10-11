# 🥗 Cal AI — Python Production Clone

Clon fiel de la experiencia de usuario de **Cal AI**, diseñado bajo principios Mobile-First, arquitectura modular en Python y capacidades multimodales con visión por computadora mediante Inteligencia Artificial (Google Gemini 2.5 Flash / OpenAI GPT-4o).

---

## 🚀 Inicio Rápido

### 1. Activar / Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno (Opcional)
Edita el archivo `.env` para añadir tu API key de Gemini o de OpenAI:
```env
GEMINI_API_KEY=tu_api_key_aqui
# o
OPENAI_API_KEY=tu_api_key_aqui
```
> *Nota: Si no introduces ninguna API key, la aplicación incluye un analizador inteligente con datos de alta precisión para pruebas.*

### 3. Ejecutar el Servidor
```bash
python main.py
```
El servidor arrancará en `http://0.0.0.0:8000`.

---

## 📱 Acceso desde Móvil / Android en Red Local
1. Abre tu consola y averigua la IP local de tu PC con `ipconfig` (ej: `192.168.1.45`).
2. Conecta tu teléfono móvil a la misma red Wi-Fi.
3. Abre Chrome en Android y navega a:
   ```
   http://192.168.1.45:8000
   ```
4. Podrás usar la cámara nativa directamente para tomar fotos a tus comidas.

---

## 📐 Estructura de Módulos
- [**`main.py`**](file:///c:/Users/alexr/OneDrive/Documentos/cal_app/main.py): Entrada principal, servidor FastAPI, endpoints y UI interactiva de Cal AI con diseño dark mode mobile-first.
- [**`nutrition_calc.py`**](file:///c:/Users/alexr/OneDrive/Documentos/cal_app/nutrition_calc.py): Fórmulas matemáticas de Mifflin-St Jeor para BMR, TDEE, déficit/superávit metabólico y distribución balanceada de macronutrientes.
- [**`database.py`**](file:///c:/Users/alexr/OneDrive/Documentos/cal_app/database.py): Capa de base de datos relacional SQLite (`user_profile` y `daily_meals`).
- [**`vision_service.py`**](file:///c:/Users/alexr/OneDrive/Documentos/cal_app/vision_service.py): Integración con visión multimodal (Gemini / OpenAI) con prompt JSON estricto y fallback.
- [**`config.py`**](file:///c:/Users/alexr/OneDrive/Documentos/cal_app/config.py): Gestión de configuración con Pydantic Settings.
