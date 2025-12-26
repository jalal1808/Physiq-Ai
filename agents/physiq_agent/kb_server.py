import sqlite3
from fastmcp import FastMCP

##Initialize FastMCP server
mcp = FastMCP("HealthKnowledgeBase")
DB_PATH = "knowledge_base.db"

def query_db(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@mcp.tool()
def search_top_doctors(city: str, speciality: str, limit: int = 3):
    """
    Finds the top N doctors in a city based on speciality.
    Results are sorted by fee (lowest first) to provide the 'best' recommendations.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Using ORDER BY fee ASC and LIMIT to get the top 3
    query = """
        SELECT name, designation, speciality, location, fee 
        FROM doctors 
        WHERE location LIKE ? AND speciality LIKE ?
        ORDER BY fee ASC
        LIMIT ?
    """
    
    cursor.execute(query, (f"%{city}%", f"%{speciality}%", limit))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No doctors found matching those criteria."
    
    return [
        {"name": r[0], "designation": r[1], "speciality": r[2], "location": r[3], "fee": r[4]} 
        for r in rows
    ]

@mcp.tool()
def get_top_exercises(muscle_group: str = None, limit: int = 3):
    """
    Finds the top N exercises based on rating.
    Can be filtered by muscle group.
    Results are sorted by rating (highest first).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT exercise_name, muscle, equipment, rating
        FROM exercises
    """

    params = []

    if muscle_group:
        query += " WHERE muscle LIKE ?"
        params.append(f"%{muscle_group}%")

    query += " ORDER BY rating DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No exercises found matching those criteria."

    return [
        {
            "exercise_name": r[0],
            "muscle": r[1],
            "equipment": r[2],
            "rating": r[3]
        }
        for r in rows
    ]

@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """Calculates BMI and returns category with the specific goal keyword."""
    if height_cm <= 0:
        return "Error: Height must be positive."
    
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m**2), 1)
    
    if bmi < 18.5:
        goal = "weight_gain"
        cat = "Underweight"
    elif 18.5 <= bmi < 25:
        goal = "weight_loss" # Defaulting to loss/maintenance
        cat = "Healthy weight"
    else:
        goal = "weight_loss"
        cat = "Overweight/Obese"
        
    return f"BMI: {bmi} ({cat}). Recommended Goal: {goal}"

@mcp.tool()
def get_top_foods(goal: str) -> str:
    """Queries the local sqlite3 DB for top foods based on weight goal."""
    try:
        conn = sqlite3.connect(DB_PATH) # Ensure DB_PATH is defined in your environment
        cursor = conn.cursor()
        
        # Protect against injection by strictly mapping the sort column
        sort_col = "weight_loss_rating" if goal == "weight_loss" else "weight_gain_rating"
        
        query = f"""
            SELECT food_item, category, calories, protein 
            FROM food 
            ORDER BY {sort_col} DESC 
            LIMIT 3
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No food data found for this goal."
            
        # Returning a formatted string the Agent can easily read
        return str([{"food": r[0], "type": r[1], "kcal": r[2], "protein": r[3]} for r in rows])
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def calculate_cumulative_sleep_debt(avg_actual_hours: float, days: int = 1, required_hours: float = 8.0):
    """
    Calculates total sleep debt over a period and provides a recovery strategy.
    """
    daily_debt = required_hours - avg_actual_hours
    total_debt = daily_debt * days
    
    # Logic based on the "Sleep Pressure" model
    if total_debt <= 0:
        status, severity = "Sustained Baseline", "None"
        guidance = "You are in a 'Sleep Surplus.' Maintain your current rhythm to protect cognitive performance."
    elif total_debt <= 4:
        status, severity = "Acute Sleep Debt", "Low"
        guidance = "Manageable. A 20-minute power nap today and an extra 30 minutes of sleep tonight will clear this."
    elif total_debt <= 10:
        status, severity = "Cumulative Fatigue", "Moderate"
        guidance = "You are likely experiencing 'micro-sleeps' or brain fog. Prioritize a consistent wake-up time and shift bedtime 45 mins earlier for 3 nights."
    else:
        status, severity = "Chronic Sleep Deprivation", "High"
        guidance = "Critical debt level. Do not attempt to 'catch up' all at once (this causes social jetlag). Aim for a consistent +1 hour per night over the next week."

    return {
        "status": status,
        "severity": severity,
        "total_debt_hours": round(total_debt, 2),
        "recovery_estimate_days": max(1, round(total_debt / 1.5)), # Estimates days to recover safely
        "guidance": guidance
    }
    
@mcp.tool()
def get_sleep_knowledge(query: str) -> str:
    """
    Queries the local sqlite3 DB for sleep-related knowledge
    based on a user query.
    """
    try:
        conn = sqlite3.connect(DB_PATH)  # Ensure DB_PATH is defined
        cursor = conn.cursor()

        sql_query = """
            SELECT question, answer, intent, category
            FROM sleep_knowledge
            WHERE question LIKE ?
               OR tags LIKE ?
               OR intent LIKE ?
            LIMIT 3
        """

        cursor.execute(
            sql_query,
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No sleep-related knowledge found for this query."

        # Agent-friendly structured response
        return str([
            {
                "matched_question": r[0],
                "answer": r[1],
                "intent": r[2],
                "category": r[3]
            }
            for r in rows
        ])

    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()