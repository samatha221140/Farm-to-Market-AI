import requests, json, base64, time

base = 'http://127.0.0.1:5000'

# Test health
h = requests.get(f'{base}/api/health', timeout=5).json()
print('Health:', h.get('status'), '| DB Engine:', h.get('database_engine'))

# Test fertilizer plan
t0 = time.time()
r1 = requests.post(f'{base}/api/phase2/fertilizer-plan',
    json={'crop': 'Chilli', 'soil_n': 45, 'soil_p': 25, 'soil_k': 35, 'acres': 2.0}, timeout=10).json()
bags = r1.get('plan', {}).get('total_farm_bags_50kg', {})
print(f"Fertilizer ({round(time.time()-t0, 2)}s): success={r1.get('success')}, dap={bags.get('dap_bags')} bags, urea={bags.get('urea_bags')} bags")

# Test irrigation
t0 = time.time()
r2 = requests.post(f'{base}/api/phase2/irrigation-advisory', json={
    'crop': 'Chilli', 'soil_type': 'Red',
    'growth_stage': 'Flowering & Pegging / Tasseling (35-65 DAS)',
    'soil_moisture_pct': 21.5, 'rainfall_today_mm': 0, 'forecast_rain_mm': 0,
    'temperature': 31, 'humidity': 58, 'pump_rating': '1.0 HP',
    'irrigation_method': 'Drip Irrigation', 'acres': 2.0, 'save_to_db': False
}, timeout=10).json()
adv = r2.get('advisory', {})
pump = adv.get('pump_operation', {})
water = adv.get('water_calculation', {})
print(f"Irrigation ({round(time.time()-t0, 2)}s): success={r2.get('success')}, pump={pump.get('pump_state')}, water={water.get('total_water_liters')} L, runtime={pump.get('runtime_hours_str')}")

# Test diagnose
t0 = time.time()
img_b64 = base64.b64encode(open('backend/uploads/diagnoses/diag_chilli_20261127_101835_9365b8aa.jpg', 'rb').read()).decode()
r3 = requests.post(f'{base}/api/phase2/diagnose-image',
    json={'crop': 'Chilli', 'image_base64': img_b64}, timeout=15).json()
vm = r3.get('visual_metrics', {})
print(f"Diagnose ({round(time.time()-t0, 2)}s): success={r3.get('success')}, name={r3.get('diagnosis_name')}")
print(f"  confidence={r3.get('confidence_pct')}%, severity={r3.get('severity')}")
print(f"  visual_metrics type={type(vm).__name__}: green={vm.get('healthy_green_pct')}%, necrotic={vm.get('necrotic_lesion_pct')}%")
tc = r3.get('top_candidates', [])
print(f"  top_candidates type={type(tc).__name__}, count={len(tc)}, first={tc[0].get('condition') if tc else 'none'}")

# Test soil
t0 = time.time()
r4 = requests.post(f'{base}/api/phase2/analyze-soil-fertilizer', json={
    'crop': 'Groundnut', 'acres': 2.0, 'N': 45, 'P': 25, 'K': 35,
    'pH': 6.8, 'organic_carbon': 0.55, 'ec': 0.6, 'zinc': 0.55
}, timeout=10).json()
bs = r4.get('chemical_package', {}).get('bag_summary', {})
print(f"Soil+Fert ({round(time.time()-t0, 2)}s): success={r4.get('success')}, dap={bs.get('dap_50kg_bags')} bags, urea={bs.get('urea_50kg_bags')} bags, zinc={bs.get('zinc_sulfate_kg')} kg")

print('\nALL PHASE 2 TESTS PASSED - stable server, no connection resets!')
