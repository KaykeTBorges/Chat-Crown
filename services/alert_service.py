from services.database import db_manager
from services.budget_service import budget_service
from services.finance_calculator import FinanceCalculator

class AlertService:
    def __init__(self):
        self.db = db_manager
        self.finance_calc = FinanceCalculator()
    
    def get_daily_budget_alerts(self, telegram_id: int):
        """Alertas baseados no orçamento diário do método Breno - CORRIGIDO"""
        daily_status = self.finance_calc.get_daily_budget_status(telegram_id)
        alerts = []
        
        # ✅ CORREÇÃO: Verificar se a estrutura existe antes de acessar
        if not daily_status or 'situacao_dias' not in daily_status:
            return alerts
        
        # Encontrar o dia atual
        dia_atual = None
        for dia in daily_status['situacao_dias']:
            if dia.get('status') == 'hoje' or 'HOJE' in str(dia.get('data', '')):
                dia_atual = dia
                break
        
        if not dia_atual:
            return alerts
        
        # ✅ CORREÇÃO: Usar as chaves corretas da estrutura existente
        today_spent = dia_atual.get('gasto', 0)
        daily_budget = dia_atual.get('meta_diaria', 0)
        
        # Alertas de orçamento diário
        if today_spent > daily_budget:
            excess = today_spent - daily_budget
            alerts.append({
                'type': 'daily_exceeded',
                'message': f"🚨 ORÇAMENTO DIÁRIO EXCEDIDO! Você gastou R$ {excess:.2f} a mais hoje",
                'severity': 'high'
            })
        elif today_spent > daily_budget * 0.8:
            alerts.append({
                'type': 'daily_warning', 
                'message': f"⚠️ Cuidado! Você já gastou {today_spent:.2f} de {daily_budget:.2f} hoje ({((today_spent/daily_budget)*100):.1f}%)",
                'severity': 'medium'
            })
        
        # ✅ CORREÇÃO: Alertas de tendência mensal com chaves corretas
        if 'dias_restantes' in daily_status and daily_status['dias_restantes'] > 0:
            remaining_budget = daily_status.get('saldo_restante_mes', 0)
            remaining_days = daily_status['dias_restantes']
            
            if remaining_days > 0 and remaining_budget > 0:
                daily_average_needed = remaining_budget / remaining_days
                if daily_average_needed > daily_budget * 1.5:
                    alerts.append({
                        'type': 'monthly_trend',
                        'message': f"📊 Atenção: Para atingir sua meta, precisa gastar apenas R$ {daily_average_needed:.2f}/dia",
                        'severity': 'medium'
                    })
        
        return alerts
    
    def get_budget_alerts(self, telegram_id: int, month: int = None, year: int = None):
        """Alertas de orçamento por categoria"""
        try:
            budget_data = budget_service.get_budgets_with_status(telegram_id, month, year)
            alerts = []
            
            for alert_msg in budget_data.get('alerts', []):
                alerts.append({
                    'type': 'budget_alert',
                    'message': alert_msg,
                    'severity': 'high' if '🚨' in alert_msg else 'medium'
                })
            
            return alerts
        except Exception as e:
            print(f"❌ Erro em get_budget_alerts: {e}")
            return []
    
    def get_economy_alerts(self, telegram_id: int, month: int = None, year: int = None):
        """Alertas de economia (método Breno) - CORRIGIDO"""
        try:
            summary = self.finance_calc.get_monthly_summary(telegram_id, month, year)
            alerts = []
            
            # ✅ CORREÇÃO: Verificar se as chaves existem
            if not summary or 'economia_real_vs_meta' not in summary:
                return alerts
            
            if summary['economia_real_vs_meta'] < 0:
                alerts.append({
                    'type': 'economy_alert',
                    'message': f"🎯 ECONOMIA ABAIXO DA META! Está R$ {abs(summary['economia_real_vs_meta']):.2f} abaixo dos 25%",
                    'severity': 'high'
                })
            elif summary['economia_real_vs_meta'] < summary.get('meta_economia', 0) * 0.1:
                alerts.append({
                    'type': 'economy_warning',
                    'message': f"💡 Faltam R$ {abs(summary['economia_real_vs_meta']):.2f} para atingir a meta de economia",
                    'severity': 'medium'
                })
            
            return alerts
        except Exception as e:
            print(f"❌ Erro em get_economy_alerts: {e}")
            return []
    
    def get_all_alerts(self, telegram_id: int, month: int = None, year: int = None):
        """Todos os alertas combinados - CORRIGIDO"""
        alerts = []
        
        try:
            alerts.extend(self.get_daily_budget_alerts(telegram_id))
            alerts.extend(self.get_budget_alerts(telegram_id, month, year))
            alerts.extend(self.get_economy_alerts(telegram_id, month, year))
            
            # Ordenar por severidade (high primeiro)
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 2))
            
            return alerts[:6]  # Limitar a 6 alertas
        except Exception as e:
            print(f"❌ Erro em get_all_alerts: {e}")
            return []

# Instância global
alert_service = AlertService()