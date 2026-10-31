# Garment & Textile Order Management System (OrderFlow)

A fullstack Django application designed using the **Django MVT (Model-View-Template)** architecture and styled with **Tailwind CSS**.

---

## 🏛️ System Hierarchy

The application strictly follows your requested hierarchy:

```
├── Job (Top Level)
│   ├── Job Number (e.g., JOB-1001)
│   ├── Buyer (e.g., Zara, H&M, Nike)
│   ├── Order ID (Auto-generated 6-digit sequence: e.g. 100001)
│   ├── Date (e.g., 2026-10-31)
│   ├── Status (Pending, In Production, Completed, Delivered)
│   └── Remarks / Instructions
│       │
│       └── Order Breakdown Items (Child Level)
│           ├── Colours (Interactive Tags: e.g. Navy Blue, Black)
│           ├── Fabric (e.g., Lycra Single Jersey, 100% Cotton Pique)
│           ├── Quantity in Pieces (e.g., 1,200 pcs)
│           ├── Sizes (Interactive Tags: e.g. S, M, L, XL, XXL)
│           └── Sub Order ID (Inherits Job's auto-generated Order ID)
```

---

## 🏷️ Interactive Tag Inputs & Auto Order ID

1. **Automatic Order ID Generation**:
   - Every new Job is automatically assigned a sequential 6-digit Order ID (e.g. `100001`, `100002`, `100003`...).
   - Can also be left blank on save, and the model auto-populates it.
   - All child order lines automatically inherit this Order ID.

2. **Interactive Tag Inputs (Colours & Sizes)**:
   - Type a name (e.g. `Navy Blue` or `S`) and press **Enter** or **comma (`,`)**.
   - It instantly converts into a tag chip (`[ Navy Blue × ]` or `[ S × ]`) and clears the text field, immediately giving you space to type other items without clicking anywhere!
   - Pressing **Backspace** on an empty input removes the previous tag.
   - Clicking `×` removes that specific tag.
   - Supports preset one-click buttons for common apparel sizes and colours.

---

## 🔍 Filtering Capabilities

The dashboard provides real-time filtering by:
1. **Date**: Filter jobs by exact production date.
2. **Buyer**: Filter by buyer/brand name (with autocomplete datalist and text search).
3. **Order ID**: Filter/search by order number (e.g. `123456`), which searches both top-level Job order numbers and nested order item lines.
4. **Combined Filtering**: Filter across any combination with active filter indicator badges and a single-click "Clear all filters" button.

---

## 🎨 Minimal & Professional Design

- **Single Background Color Theme**: Monochromatic Slate palette (`#f1f5f9` / Slate-100).
- **Light Variations**: Pure white (`#ffffff`) cards, soft slate badges (`#f8fafc`), and subtle borders (`#e2e8f0`).
- **Typography & Accents**: High-contrast, executive slate (`#0f172a`), clean badges, and clear visual hierarchy.
- **No Clutter**: Distraction-free interface optimized for daily operations in garment manufacturing and apparel merchandising.

---

## 🚀 Getting Started

### 1. Activate Environment & Run Server
```bash
# In the project directory:
.venv\Scripts\activate

# Start the development server:
python manage.py runserver
```

Open your browser at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

### 2. Admin Panel Access
- **URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Username**: `admin`
- **Password**: `admin123`

### 3. Load Sample Demo Data
You can click the **"Load Demo Data"** button in the top navigation bar or run:
```bash
python manage.py seed_data
```
This loads realistic apparel data including Lycra Single Jersey, 100% Cotton Pique, French Terry, and multiple buyers.

### 4. Run Automated Tests
```bash
python manage.py test jobs
```
All 8 test cases verify models, relationships, order ID inheritance, and filtering logic.

