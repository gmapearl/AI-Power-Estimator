import streamlit as st
import tiktoken

# Constants (estimates based on typical model usage and data center efficiency)
ENERGY_PER_TOKEN_WATTS = {
    'gpt-4': 0.0025,
    'gpt-3.5': 0.0020,
    'claude-2': 0.0018,
    'claude-3': 0.0017,
    'gemini-1': 0.0015,
    'gemini-1.5': 0.0014,
    'mistral': 0.0020,
    'mixtral': 0.0019,
    'llama-2-13b': 0.0022,
    'llama-3-70b': 0.0024
}

WATER_PER_KWH_LITERS = 1.8  # liters per kWh (for cooling)

# Energy estimation function
def estimate_energy_usage(model, token_count):
    watts = ENERGY_PER_TOKEN_WATTS[model] * token_count
    return watts / 1000  # watt-hours

# Water usage estimation
def estimate_water_usage(energy_wh):
    return (energy_wh / 1000) * WATER_PER_KWH_LITERS

# Tokenizer (uses tiktoken for OpenAI models and heuristics for others)
def count_tokens(text, model):
    if model in ['gpt-4', 'gpt-3.5']:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    elif 'claude' in model:
        return int(len(text.split()) * 1.1)
    elif 'gemini' in model:
        return int(len(text.split()) * 1.0)
    elif 'mistral' in model or 'mixtral' in model:
        return int(len(text.split()) * 1.3)
    elif 'llama' in model:
        return int(len(text.split()) * 1.25)
    else:
        return int(len(text.split()) * 1.3)

# Streamlit UI
st.title("AI Token Impact Calculator")
st.markdown("Estimate your prompt's **energy and water footprint**, and get a recommendation for the most efficient model.")

# Input field
prompt = st.text_area("Paste Your Prompt Here", height=200)

if prompt:
    results = []
    for model in ENERGY_PER_TOKEN_WATTS.keys():
        token_count = int(count_tokens(prompt, model))
        energy_wh = estimate_energy_usage(model, token_count)
        water_liters = estimate_water_usage(energy_wh)
        results.append({
            'model': model,
            'tokens': token_count,
            'energy_wh': energy_wh,
            'water_liters': water_liters
        })

    # Sort by energy use (lower is better)
    sorted_results = sorted(results, key=lambda x: x['energy_wh'])
    best_model = sorted_results[0]['model']

    # User selection
    selected_model = st.selectbox("Select a Model to View Stats", [r['model'] for r in sorted_results])
    selected_stats = next(r for r in sorted_results if r['model'] == selected_model)

    # Results display
    st.subheader("Estimated Impact")
    st.metric("Token Count", f"{selected_stats['tokens']} tokens")
    st.metric("Energy Consumption (Wh)", f"{selected_stats['energy_wh']:.4f}")
    st.metric("Water Usage (Liters)", f"{selected_stats['water_liters']:.4f}")

    st.success(f"✅ Most Efficient Model for this Prompt: {best_model}")
    st.info("💡 Fewer tokens = Less compute = Lower environmental impact. Try tightening your prompt without losing clarity!")
else:
    st.warning("Enter a prompt above to see model efficiency comparisons.")
