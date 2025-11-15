import re
import json
from groq import Groq
from config.config import config
from datetime import datetime

class AIProcessor:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None
        self.setup_categories()
    
    def setup_categories(self):
        self.categories = {
            'despesas_fixas': {
                'Moradia': ['aluguel', 'luz', 'água', 'condomínio', 'internet', 'telefone', 'gás'],
                'Transporte': ['ônibus', 'metro', 'uber', 'taxi', 'combustível', 'estacionamento'],
                'Saúde': ['plano de saúde', 'médico', 'dentista', 'farmácia', 'remédio', 'academia'],
                'Educação': ['faculdade', 'curso', 'livro', 'material'],
                'Seguros': ['seguro', 'previdência'],
                'Dívidas': ['financiamento', 'empréstimo', 'parcela']
            },
            'despesas_variaveis': {
                'Alimentação': ['almoço', 'janta', 'lanche', 'mercado', 'supermercado', 'restaurante', 'ifood'],
                'Lazer': ['cinema', 'netflix', 'spotify', 'shopping', 'bar', 'viagem'],
                'Vestuário': ['roupa', 'sapato', 'camisa', 'calça'],
                'Diversos': ['presente', 'doação', 'reparo', 'manutenção']
            },
            'rendas': {
                'Salário': ['salário', 'salario', 'contracheque'],
                'Freela': ['freela', 'freelance', 'projeto'],
                'Investimentos': ['dividendos', 'renda', 'investimento', 'juros'],
                'Outros': ['extra', 'bônus', 'presente', 'doação']
            },
            'economia': {
                'Investimentos': ['investi', 'apliquei', 'comprei ações', 'tesouro', 'cdb', 'fii'],
                'Poupança': ['poupança', 'poupanca', 'guardei', 'reserva', 'emergência'],
                'Fundos': ['fundo', 'fundo de investimento', 'etf'],
                'Previdência': ['previdência', 'privada', 'aposentadoria']
            }
        }
    
    def detect_expense(self, message: str) -> dict:
        regex_result = self._detect_with_regex(message)
        
        if regex_result['amount'] is None and self.client:
            try:
                ai_result = self._detect_with_ai(message)
                if ai_result['confidence'] > 0.7:
                    return ai_result
            except Exception as e:
                print(f"❌ Erro na IA: {e}. Continuando com regex...")
        
        return regex_result
    
    def _detect_with_regex(self, message: str) -> dict:
        amount_patterns = [
            r'R\$\s*(\d+[.,]\d{2})',
            r'R\$\s*(\d+)',
            r'(\d+[.,]\d{2})',
            r'(\d+)'
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, message)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        message_lower = message.lower()
        category = "Diversos"
        type_ = "despesa_variavel"
        confidence = 0.6
        
        for cat_name, keywords in self.categories['rendas'].items():
            for keyword in keywords:
                if keyword in message_lower:
                    category = cat_name
                    type_ = "renda"
                    confidence = 0.9
                    break
        
        if type_ != "renda":
            for cat_name, keywords in self.categories['economia'].items():
                for keyword in keywords:
                    if keyword in message_lower:
                        category = cat_name
                        type_ = "economia"
                        confidence = 0.9
                        break
        
        if type_ not in ['renda', 'economia']:
            for cat_name, keywords in self.categories['despesas_fixas'].items():
                for keyword in keywords:
                    if keyword in message_lower:
                        category = cat_name
                        type_ = "despesa_fixa"
                        confidence = 0.8
                        break
            
            if type_ == "despesa_variavel":
                for cat_name, keywords in self.categories['despesas_variaveis'].items():
                    for keyword in keywords:
                        if keyword in message_lower:
                            category = cat_name
                            confidence = 0.7
                            break
        
        description = re.sub(r'R\$\s*\d+[.,]?\d*', '', message).strip()
        description = re.sub(r'\d+[.,]?\d*', '', description).strip()
        
        return {
            "amount": amount,
            "category": category,
            "type": type_,
            "description": description if description else "Despesa",
            "confidence": confidence,
            "detected_by": "regex"
        }
    
    def _detect_with_ai(self, message: str) -> dict:
        prompt = f"""
        Analise esta mensagem financeira e retorne APENAS JSON:

        Mensagem: "{message}"

        Categorias FIXAS: {list(self.categories['despesas_fixas'].keys())}
        Categorias VARIÁVEIS: {list(self.categories['despesas_variaveis'].keys())}
        Categorias RENDA: {list(self.categories['rendas'].keys())}
        Categorias ECONOMIA: {list(self.categories['economia'].keys())}

        Regras:
        - Se for aluguel, conta de casa, parcela fixa → FIXA
        - Se for comida, transporte, compras do dia → VARIÁVEL  
        - Se for salário, recebimento → RENDA
        - Se for investimento, poupança, guardar dinheiro → ECONOMIA
        - Extraia o valor numérico (pode ter R$, pontos, vírgulas)
        - Descrição resumida em 2-3 palavras

        Retorne JSON: {{"amount": float, "category": string, "type": "fixa"|"variavel"|"renda"|"economia", "description": string, "confidence": float}}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            result['detected_by'] = 'groq'
            return result
            
        except Exception as e:
            raise Exception(f"Erro Groq AI: {e}")

ai_processor = AIProcessor()