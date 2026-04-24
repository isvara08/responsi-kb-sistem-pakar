"""
Sistem Pakar Diagnosis Gangguan Suara (Disfonia)
Metode: Certainty Factor dengan Forward Chaining
Backend: Python Flask API
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

# ============================================================================
# KNOWLEDGE BASE - BASIS PENGETAHUAN
# ============================================================================

class KnowledgeBase:
    """Knowledge Base berisi gejala dan aturan diagnosis"""
    
    # Gejala Disfonia (15 gejala)
    SYMPTOMS = {
        'G1': {'name': 'Suara serak (hoarseness)', 'code': 'serak'},
        'G2': {'name': 'Suara pecah-pecah', 'code': 'pecah'},
        'G3': {'name': 'Sakit atau nyeri saat berbicara', 'code': 'nyeri'},
        'G4': {'name': 'Sulit meninggikan suara', 'code': 'sulit_tinggi'},
        'G5': {'name': 'Batuk kronis', 'code': 'batuk'},
        'G6': {'name': 'Globus sensation (terasa ada benjolan di tenggorokan)', 'code': 'globus'},
        'G7': {'name': 'Suara lemah atau tidak bertenaga', 'code': 'lemah'},
        'G8': {'name': 'Kehabisan napas saat berbicara', 'code': 'napas'},
        'G9': {'name': 'Suara terdengar tegang/straining', 'code': 'tegang'},
        'G10': {'name': 'Nyeri leher atau jaw', 'code': 'nyeri_leher'},
        'G11': {'name': 'Suara mendesis (breathy voice)', 'code': 'mendesis'},
        'G12': {'name': 'Demam dan pilek', 'code': 'demam'},
        'G13': {'name': 'Penurunan jangkauan nada suara', 'code': 'nada'},
        'G14': {'name': 'Suara terputus-putus', 'code': 'putus'},
        'G15': {'name': 'Mual atau refluks asam', 'code': 'refluks'}
    }
    
    # Jenis Disfonia dengan CF Pakar untuk setiap gejala
    DISEASES = {
        'Nodul Pita Suara': {
            'code': 'P1',
            'symptoms': {
                'G1': 0.9,   # Suara serak
                'G2': 0.8,   # Suara pecah-pecah
                'G3': 0.7,   # Nyeri saat bicara
                'G4': 0.8,   # Sulit tinggi
                'G9': 0.6,   # Tegang
                'G13': 0.7   # Nada turun
            },
            'icon': 'fa-head-side-cough',
            'category': 'Organik',
            'description': 'Pertumbuhan jinak pada pita suara akibat penggunaan suara berlebihan atau salah teknik vokal.',
            'recommendations': [
                'Istirahatkan suara minimal 7-14 hari',
                'Hindari berbicara terlalu keras atau terlalu lama',
                'Lakukan pemanasan vokal sebelum menyanyi',
                'Konsultasi dengan dokter THT untuk terapi vokal',
                'Jika parah, mungkin memerlukan operasi mikrokirurgi'
            ]
        },
        'Polip Pita Suara': {
            'code': 'P2',
            'symptoms': {
                'G1': 0.9,   # Suara serak
                'G11': 0.8,  # Mendesis
                'G2': 0.7,   # Pecah
                'G4': 0.9,   # Sulit tinggi
                'G7': 0.8    # Lemah
            },
            'icon': 'fa-water',
            'category': 'Organik',
            'description': 'Benjolan seperti kantung berisi cairan pada pita suara, biasanya pada satu sisi.',
            'recommendations': [
                'Istirahat vokal total jika diperlukan',
                'Hindari merokok dan paparan iritan',
                'Terapi vokal dengan terapis berlisensi',
                'Evaluasi operasi jika ukuran polip besar',
                'Kontrol faktor risiko seperti refluks'
            ]
        },
        'Kelelahan Vokal': {
            'code': 'P3',
            'symptoms': {
                'G7': 0.9,   # Lemah
                'G8': 0.8,   # Napas habis
                'G9': 0.7,   # Tegang
                'G1': 0.6,   # Serak
                'G3': 0.5,   # Nyeri
                'G10': 0.6   # Nyeri leher
            },
            'icon': 'fa-tired',
            'category': 'Fungsional',
            'description': 'Kelelahan otot laring akibat penggunaan suara intensif tanpa istirahat yang cukup.',
            'recommendations': [
                'Istirahatkan suara secara teratur',
                'Gunakan teknik pernapasan diafragma',
                'Hidrasi yang cukup (8-10 gelas air/hari)',
                'Tidur yang cukup 7-8 jam per malam',
                'Lakukan pemanasan dan pendinginan vokal'
            ]
        },
        'Laringitis': {
            'code': 'P4',
            'symptoms': {
                'G1': 0.9,   # Serak
                'G12': 0.8,  # Demam
                'G3': 0.7,   # Nyeri
                'G2': 0.6,   # Pecah
                'G11': 0.5   # Mendesis
            },
            'icon': 'fa-fire',
            'category': 'Organik',
            'description': 'Radang pada pita suara akibat infeksi virus, bakteri, atau penggunaan suara berlebihan.',
            'recommendations': [
                'Istirahat suara total selama 3-5 hari',
                'Minum air hangat dengan madu',
                'Hindari minuman dingin dan berkafein',
                'Gunakan pelembab udara',
                'Jika tidak membaik dalam seminggu, periksakan ke dokter'
            ]
        },
        'Disfonia Muscle Tension': {
            'code': 'P5',
            'symptoms': {
                'G9': 0.9,   # Tegang
                'G10': 0.8,  # Nyeri leher
                'G3': 0.7,   # Nyeri
                'G7': 0.6,   # Lemah
                'G6': 0.7,   # Globus
                'G14': 0.6   # Putus
            },
            'icon': 'fa-exclamation-triangle',
            'category': 'Fungsional',
            'description': 'Ketegangan otot laring yang berlebihan akibat stres atau teknik vokal salah.',
            'recommendations': [
                'Terapi vokal dengan terapis wicara',
                'Teknik relaksasi dan manajemen stres',
                'Latihan pelepasan ketegangan otot leher',
                'Pijat leher dan bahu secara teratur',
                'Yoga atau meditasi untuk mengurangi stres'
            ]
        },
        'Refluks Laringofaringeal': {
            'code': 'P6',
            'symptoms': {
                'G6': 0.9,   # Globus
                'G15': 0.8,  # Refluks
                'G1': 0.7,   # Serak
                'G3': 0.6,   # Nyeri
                'G11': 0.5   # Mendesis
            },
            'icon': 'fa-stomach',
            'category': 'Organik',
            'description': 'Refluks asam lambung yang mengiritasi laring tanpa gejala maag yang jelas.',
            'recommendations': [
                'Hindari makan 3 jam sebelum tidur',
                'Kurangi makanan pedas, asam, dan berlemak',
                'Angkat kepala tempat tidur 15-20 cm',
                'Obat penghambat asam sesuai resep dokter',
                'Konsultasi dengan dokter THT atau gastroenterolog'
            ]
        },
        'Papiloma Laring': {
            'code': 'P7',
            'symptoms': {
                'G1': 0.8,   # Serak
                'G4': 0.9,   # Sulit tinggi
                'G2': 0.7,   # Pecah
                'G8': 0.6,   # Napas
                'G14': 0.7   # Putus
            },
            'icon': 'fa-wave-square',
            'category': 'Organik',
            'description': 'Pertumbuhan seperti kutil pada laring akibat virus HPV.',
            'recommendations': [
                'Evaluasi operasi untuk pembuangan jaringan',
                'Terapi antiviral sesuai indikasi',
                'Pemantauan endoskopi rutin',
                'Vaksinasi HPV untuk pencegahan',
                'Terapi laser atau cryosurgery'
            ]
        },
        'Paralisis Pita Suara': {
            'code': 'P8',
            'symptoms': {
                'G11': 0.9,  # Mendesis
                'G7': 0.9,   # Lemah
                'G4': 0.8,   # Sulit tinggi
                'G8': 0.8,   # Napas
                'G2': 0.6    # Pecah
            },
            'icon': 'fa-arrows-alt-h',
            'category': 'Organik',
            'description': 'Kelemahan atau kelumpuhan pita suara akibat kerusakan saraf laring.',
            'recommendations': [
                'Evaluasi neurologi dan THT menyeluruh',
                'Terapi vokal untuk kompensasi',
                'Injeksi filler untuk pita suara',
                'Tiroplasti untuk meningkatkan tekanan glotis',
                'Fisioterapi vokal intensif'
            ]
        }
    }


# ============================================================================
# CERTAINTY FACTOR ENGINE
# ============================================================================

class CertaintyFactorEngine:
    """Mesin Certainty Factor dengan Forward Chaining"""
    
    @staticmethod
    def calculate_cf(cf_pakar, cf_user):
        """
        Menghitung CF untuk satu aturan
        Rumus: CF(H,E) = CF(Pakar) * CF(User)
        """
        return cf_pakar * cf_user
    
    @staticmethod
    def combine_cf(cf1, cf2):
        """
        Menggabungkan dua nilai CF
        Rumus: CFcombine = CF1 + CF2 * (1 - CF1)
        """
        return cf1 + cf2 * (1 - cf1)
    
    @classmethod
    def forward_chaining(cls, selected_symptoms):
        """
        Forward Chaining: Mencocokkan gejala dengan aturan untuk mencapai diagnosis
        
        Args:
            selected_symptoms: dict {symptom_id: cf_user_value}
        
        Returns:
            list of tuples (disease_name, cf_value) sorted by CF descending
        """
        results = {}
        kb = KnowledgeBase()
        
        # Iterasi setiap penyakit (Forward Chaining dari gejala ke diagnosis)
        for disease_name, disease_data in kb.DISEASES.items():
            cf_combined = 0.0
            has_matching_symptom = False
            
            # Cek setiap gejala penyakit
            for symptom_id, cf_pakar in disease_data['symptoms'].items():
                if symptom_id in selected_symptoms:
                    has_matching_symptom = True
                    cf_user = selected_symptoms[symptom_id]
                    
                    # Hitung CF untuk gejala ini
                    cf_rule = cls.calculate_cf(cf_pakar, cf_user)
                    
                    # Kombinasikan dengan CF yang sudah ada
                    cf_combined = cls.combine_cf(cf_combined, cf_rule)
            
            # Simpan hasil jika ada gejala yang cocok
            if has_matching_symptom:
                results[disease_name] = cf_combined
        
        # Urutkan berdasarkan CF tertinggi
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results
    
    @classmethod
    def get_detailed_analysis(cls, selected_symptoms):
        """
        Mendapatkan analisis detail untuk setiap penyakit
        """
        results = cls.forward_chaining(selected_symptoms)
        kb = KnowledgeBase()
        detailed_results = []
        
        for disease_name, cf_value in results:
            disease_data = kb.DISEASES[disease_name]
            
            # Hitung gejala yang cocok
            matched_symptoms = []
            for symptom_id in selected_symptoms:
                if symptom_id in disease_data['symptoms']:
                    symptom_name = kb.SYMPTOMS[symptom_id]['name']
                    cf_pakar = disease_data['symptoms'][symptom_id]
                    cf_user = selected_symptoms[symptom_id]
                    cf_result = cls.calculate_cf(cf_pakar, cf_user)
                    matched_symptoms.append({
                        'id': symptom_id,
                        'name': symptom_name,
                        'cf_pakar': cf_pakar,
                        'cf_user': cf_user,
                        'cf_result': cf_result
                    })
            
            detailed_results.append({
                'disease_name': disease_name,
                'disease_code': disease_data['code'],
                'cf_value': cf_value,
                'cf_percentage': round(cf_value * 100, 2),
                'category': disease_data['category'],
                'icon': disease_data['icon'],
                'description': disease_data['description'],
                'recommendations': disease_data['recommendations'],
                'matched_symptoms': matched_symptoms,
                'total_symptoms': len(disease_data['symptoms']),
                'matched_count': len(matched_symptoms)
            })
        
        return detailed_results


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main HTML file"""
    return render_template('index.html')


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """API endpoint untuk mendapatkan daftar gejala"""
    kb = KnowledgeBase()
    return jsonify({
        'success': True,
        'data': kb.SYMPTOMS
    })


@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """API endpoint untuk mendapatkan daftar penyakit"""
    kb = KnowledgeBase()
    diseases_list = []
    
    for name, data in kb.DISEASES.items():
        diseases_list.append({
            'name': name,
            'code': data['code'],
            'category': data['category'],
            'icon': data['icon'],
            'description': data['description'],
            'symptoms_count': len(data['symptoms'])
        })
    
    return jsonify({
        'success': True,
        'count': len(diseases_list),
        'data': diseases_list
    })


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """
    API endpoint untuk diagnosis
    
    Request Body:
    {
        "symptoms": {
            "G1": 0.8,
            "G2": 0.6,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'Data gejala tidak ditemukan'
            }), 400
        
        selected_symptoms = data['symptoms']
        
        if not selected_symptoms:
            return jsonify({
                'success': False,
                'error': 'Pilih minimal satu gejala'
            }), 400
        
        # Run diagnosis dengan Forward Chaining dan Certainty Factor
        engine = CertaintyFactorEngine()
        results = engine.get_detailed_analysis(selected_symptoms)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Tidak dapat menentukan diagnosis dari gejala yang diberikan'
            }), 400
        
        # Primary diagnosis (highest CF)
        primary = results[0]
        
        # Interpretasi CF
        if primary['cf_value'] >= 0.8:
            interpretation = 'Sangat Mungkin'
        elif primary['cf_value'] >= 0.6:
            interpretation = 'Mungkin'
        elif primary['cf_value'] >= 0.4:
            interpretation = 'Cukup Mungkin'
        elif primary['cf_value'] >= 0.2:
            interpretation = 'Kurang Mungkin'
        else:
            interpretation = 'Tidak Pasti'
        
        return jsonify({
            'success': True,
            'primary_diagnosis': {
                'disease': primary['disease_name'],
                'code': primary['disease_code'],
                'cf_value': primary['cf_value'],
                'cf_percentage': primary['cf_percentage'],
                'interpretation': interpretation,
                'category': primary['category'],
                'icon': primary['icon'],
                'description': primary['description'],
                'recommendations': primary['recommendations']
            },
            'all_results': results,
            'interpretation_guide': {
                '0.8-1.0': 'Sangat Mungkin - Segera konsultasi dokter',
                '0.6-0.8': 'Mungkin - Perlu perhatian dan pengobatan',
                '0.4-0.6': 'Cukup Mungkin - Pantau kondisi dan istirahat',
                '0.2-0.4': 'Kurang Mungkin - Tetap jaga kesehatan vokal',
                '0.0-0.2': 'Tidak Pasti - Data tidak cukup'
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules', methods=['GET'])
def get_rules():
    """API endpoint untuk melihat basis aturan (rule base)"""
    kb = KnowledgeBase()
    rules = []
    
    for disease_name, disease_data in kb.DISEASES.items():
        for symptom_id, cf_pakar in disease_data['symptoms'].items():
            symptom_name = kb.SYMPTOMS[symptom_id]['name']
            rules.append({
                'rule_id': f'R{len(rules)+1}',
                'if_symptom': symptom_name,
                'symptom_id': symptom_id,
                'then_disease': disease_name,
                'disease_code': disease_data['code'],
                'cf_pakar': cf_pakar,
                'rule_text': f'IF {symptom_name} THEN {disease_name} (CF={cf_pakar})'
            })
    
    return jsonify({
        'success': True,
        'total_rules': len(rules),
        'data': rules
    })


@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint untuk memeriksa status API"""
    kb = KnowledgeBase()
    
    return jsonify({
        'success': True,
        'message': 'Sistem Pakar Disfonia API is running',
        'stats': {
            'total_symptoms': len(kb.SYMPTOMS),
            'total_diseases': len(kb.DISEASES),
            'total_rules': sum(len(d['symptoms']) for d in kb.DISEASES.values()),
            'method': 'Certainty Factor with Forward Chaining'
        }
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SISTEM PAKAR DIAGNOSIS GANGGUAN SUARA (DISFONIA)")
    print("Metode: Certainty Factor dengan Forward Chaining")
    print("=" * 60)
    print(f"\nKnowledge Base:")
    kb = KnowledgeBase()
    print(f"  - Total Gejala: {len(kb.SYMPTOMS)}")
    print(f"  - Total Penyakit: {len(kb.DISEASES)}")
    print(f"  - Total Aturan: {sum(len(d['symptoms']) for d in kb.DISEASES.values())}")
    print("\nServer running at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
