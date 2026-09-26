import streamlit as st
import pandas as pd
import json
import database as db

st.set_page_config(page_title="Utapan Pricing Calculator", page_icon="🥖", layout="wide")

# Password Protection Gate
def check_password():
    def password_entered():
        if st.session_state["password_input"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Restricted Access")
    st.text_input(
        "Enter password to access the application:", 
        type="password", 
        on_change=password_entered, 
        key="password_input"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Incorrect password. Please try again.")
        
    return False

if check_password():
    db.init_db()

    st.title("🥖 Utapan Cost & Retail Price Calculator")
    st.write("An application to calculate retail prices per kg based on Food Cost, Fixed Overhead, Labor, and Profit Margins.")

    # Sidebar: General Parameters
    st.sidebar.header("⚙️ General Settings")
    monthly_prod_kg = st.sidebar.number_input(
        "Estimated Monthly Output (kg):", 
        min_value=1.0, 
        value=1000.0, 
        step=50.0
    )
    hourly_labor_cost = st.sidebar.number_input(
        "Hourly Labor/Owner Wage (€/h):", 
        min_value=0.0, 
        value=12.0, 
        step=1.0
    )

    fixed_costs_list = db.get_fixed_costs()
    total_fixed_costs_monthly = sum(c[2] for c in fixed_costs_list)
    fixed_incidence_per_kg = total_fixed_costs_monthly / monthly_prod_kg if monthly_prod_kg > 0 else 0

    st.sidebar.markdown("---")
    st.sidebar.metric("Total Monthly Overhead", f"€ {total_fixed_costs_monthly:.2f}")
    st.sidebar.metric("Fixed Overhead / kg", f"€ {fixed_incidence_per_kg:.2f} / kg")

    tab1, tab2, tab3 = st.tabs(["📝 Recipe Calculator", "🌾 Raw Materials List", "🏢 Monthly Fixed Overhead"])

    # --- TAB 1: RECIPE CALCULATOR ---
    with tab1:
        st.subheader("Recipe Costing & Saved Recipes")
        
        # Load saved recipe dropdown
        saved_recipes = db.get_recipes()
        recipe_options = ["-- New / Custom Recipe --"] + [r[1] for r in saved_recipes]
        selected_recipe_name = st.selectbox("📂 Load Saved Recipe:", recipe_options)

        if "recipe_items" not in st.session_state:
            st.session_state.recipe_items = [
                {"ingredient": "Type 0 Flour", "dose": 6.5},
                {"ingredient": "Water", "dose": 4.5},
                {"ingredient": "Fresh Yeast", "dose": 0.1},
                {"ingredient": "Fine Sea Salt", "dose": 0.13},
                {"ingredient": "Paper Bags", "dose": 10.0}
            ]

        loaded_yield = 10.0
        loaded_hours = 1.0
        loaded_margin = 30.0
        default_name = "Classic White Bread"

        if selected_recipe_name != "-- New / Custom Recipe --":
            match = next(r for r in saved_recipes if r[1] == selected_recipe_name)
            default_name = match[1]
            loaded_yield = match[2]
            loaded_hours = match[3]
            loaded_margin = match[4]
            st.session_state.recipe_items = json.loads(match[5])

        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            recipe_name = st.text_input("Product / Recipe Name:", value=default_name)
        with col_r2:
            batch_yield_kg = st.number_input("Batch Yield (kg):", min_value=0.1, value=loaded_yield, step=0.5)

        st.markdown("##### Ingredient Breakdown")
        
        ingredients_db = db.get_ingredients()
        if not ingredients_db:
            st.warning("No ingredients available. Please add ingredients in the 'Raw Materials List' tab.")
        else:
            df_ing = pd.DataFrame(ingredients_db, columns=["ID", "Name", "Category", "Price", "Qty", "Unit", "Unit Cost"])

            col_add, col_clear = st.columns([1, 5])
            if col_add.button("➕ Add Ingredient Row"):
                st.session_state.recipe_items.append({"ingredient": df_ing["Name"].iloc[0], "dose": 1.0})
                st.rerun()

            total_food_cost_batch = 0.0

            for idx, item in enumerate(st.session_state.recipe_items):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 2, 1])
                
                ing_index = df_ing["Name"].tolist().index(item["ingredient"]) if item["ingredient"] in df_ing["Name"].tolist() else 0
                selected_ing = c1.selectbox(f"Ingredient {idx+1}", df_ing["Name"].tolist(), index=ing_index, key=f"ing_{idx}")
                
                row_match = df_ing[df_ing["Name"] == selected_ing].iloc[0]
                unit = row_match["Unit"]
                unit_cost = row_match["Unit Cost"]
                
                dose = c2.number_input(f"Amount ({unit})", min_value=0.0, value=float(item["dose"]), step=0.1, key=f"dose_{idx}")
                
                row_cost = dose * unit_cost
                total_food_cost_batch += row_cost
                
                c3.write(f"€ {unit_cost:.3f}/{unit}")
                c4.write(f"**€ {row_cost:.2f}**")
                
                if c5.button("🗑️", key=f"del_{idx}"):
                    st.session_state.recipe_items.pop(idx)
                    st.rerun()

            st.markdown("---")
            st.markdown("##### Labor & Target Margin Parameters")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            labor_hours = col_m1.number_input("Preparation Time (Hours):", min_value=0.0, value=loaded_hours, step=0.25)
            target_margin = col_m2.number_input("Desired Profit Margin (%):", min_value=0.0, max_value=100.0, value=loaded_margin, step=5.0)
            vat_rate = col_m3.number_input("VAT / Sales Tax (%):", min_value=0.0, value=4.0, step=1.0)

            # CALCULATIONS
            food_cost_per_kg = total_food_cost_batch / batch_yield_kg
            labor_cost_batch = labor_hours * hourly_labor_cost
            labor_cost_per_kg = labor_cost_batch / batch_yield_kg
            
            total_prod_cost_per_kg = food_cost_per_kg + labor_cost_per_kg + fixed_incidence_per_kg
            
            pre_tax_price_per_kg = total_prod_cost_per_kg / (1 - (target_margin / 100)) if target_margin < 100 else total_prod_cost_per_kg
            vat_amount = pre_tax_price_per_kg * (vat_rate / 100)
            final_retail_price_per_kg = pre_tax_price_per_kg + vat_amount

            st.markdown("---")
            st.subheader("📊 Cost Breakdown & Pricing Summary")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Food Cost / kg", f"€ {food_cost_per_kg:.2f}")
            m2.metric("Labor / kg", f"€ {labor_cost_per_kg:.2f}")
            m3.metric("Fixed Overhead / kg", f"€ {fixed_incidence_per_kg:.2f}")
            m4.metric("Total Production Cost / kg", f"€ {total_prod_cost_per_kg:.2f}")

            st.success(f"### 💶 Recommended Retail Price: **€ {final_retail_price_per_kg:.2f} / kg** (incl. VAT)")

            st.markdown("---")
            col_save, col_del = st.columns([2, 1])
            if col_save.button("💾 Save / Update Recipe in Database"):
                if recipe_name:
                    current_items = [{"ingredient": st.session_state[f"ing_{i}"], "dose": st.session_state[f"dose_{i}"]} for i in range(len(st.session_state.recipe_items))]
                    db.save_recipe(recipe_name, batch_yield_kg, labor_hours, target_margin, current_items)
                    st.success(f"Recipe '{recipe_name}' saved successfully!")
                    st.rerun()
                else:
                    st.error("Please provide a recipe name before saving.")

            if selected_recipe_name != "-- New / Custom Recipe --":
                if col_del.button("🗑️ Delete Selected Recipe"):
                    match_del = next(r for r in saved_recipes if r[1] == selected_recipe_name)
                    db.delete_recipe(match_del[0])
                    st.success(f"Recipe '{selected_recipe_name}' deleted.")
                    st.rerun()

    # --- TAB 2: RAW MATERIALS LIST ---
    with tab2:
        st.subheader("Raw Materials Management")
        
        col_in1, col_in2 = st.columns([2, 1])
        with col_in1:
            ing_data = db.get_ingredients()
            if ing_data:
                df_ing_table = pd.DataFrame(ing_data, columns=["ID", "Name", "Category", "Purchase Price (€)", "Quantity", "Unit", "Unit Cost (€)"])
                st.dataframe(df_ing_table.drop(columns=["ID"]), use_container_width=True)
                
                del_id = st.selectbox("Select ID to delete:", df_ing_table["ID"].tolist())
                if st.button("Delete Ingredient"):
                    db.delete_ingredient(del_id)
                    st.rerun()

        with col_in2:
            st.markdown("##### Add / Update Ingredient")
            with st.form("form_ingredient"):
                nome_i = st.text_input("Ingredient Name")
                cat_i = st.selectbox("Category", ["Flours", "Leavening", "Liquids", "Seasoning", "Packaging", "Other"])
                prezzo_i = st.number_input("Purchase Price (€)", min_value=0.0, step=1.0)
                qta_i = st.number_input("Purchased Quantity", min_value=0.01, step=1.0)
                unita_i = st.selectbox("Unit of Measure", ["kg", "L", "pcs", "g"])
                
                submitted_i = st.form_submit_button("Save Ingredient")
                if submitted_i and nome_i:
                    db.add_ingredient(nome_i, cat_i, prezzo_i, qta_i, unita_i)
                    st.success("Ingredient saved successfully!")
                    st.rerun()

    # --- TAB 3: MONTHLY OVERHEAD ---
    with tab3:
        st.subheader("Fixed Monthly Operating Costs")
        
        col_cf1, col_cf2 = st.columns([2, 1])
        with col_cf1:
            cf_data = db.get_fixed_costs()
            if cf_data:
                df_cf_table = pd.DataFrame(cf_data, columns=["ID", "Expense Item", "Monthly Amount (€)"])
                st.dataframe(df_cf_table.drop(columns=["ID"]), use_container_width=True)
                
                del_cf_id = st.selectbox("Select ID to delete:", df_cf_table["ID"].tolist())
                if st.button("Delete Overhead Item"):
                    db.delete_fixed_cost(del_cf_id)
                    st.rerun()

        with col_cf2:
            st.markdown("##### Add / Update Fixed Cost")
            with st.form("form_fixed_cost"):
                voce_cf = st.text_input("Expense Item")
                importo_cf = st.number_input("Monthly Amount (€)", min_value=0.0, step=10.0)
                
                submitted_cf = st.form_submit_button("Save Expense")
                if submitted_cf and voce_cf:
                    db.add_fixed_cost(voce_cf, importo_cf)
                    st.success("Fixed expense saved!")
                    st.rerun()
