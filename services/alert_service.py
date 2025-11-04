from services.database import db_manager
from services.budget_service import budget_service
from services.finance_calculator import FinanceCalculator

class AlertService:
    def __init__(self):
        self.db = db_manager
        self.finance_calc = FinanceCalculator()
    
    def get_daily_budget_alerts(self, user_id: int):
        """Alertas baseados no orçamento diário do método Breno"""
        daily_status = self.finance_calc.get_daily_budget_status(user_id)
        alerts = []
        
        # Alertas de orçamento diário
        if daily_status['today_spent'] > daily_status['daily_budget']:
            excess = daily_status['today_spent'] - daily_status['daily_budget']
            alerts.append({
                'type': 'daily_exceeded',
                'message': f"🚨 ORÇAMENTO DIÁRIO EXCEDIDO! Você gastou R$ {excess:.2f} a mais hoje",
                'severity': 'high'
            })
        elif daily_status['today_spent'] > daily_status['daily_budget'] * 0.8:
            alerts.append({
                'type': 'daily_warning', 
                'message': f"⚠️ Cuidado! Você já gastou {daily_status['today_spent']:.2f} de {daily_status['daily_budget']:.2f} hoje ({((daily_status['today_spent']/daily_status['daily_budget'])*100):.1f}%)",
                'severity': 'medium'
            })
        
        # Alertas de tendência mensal
        if daily_status['remaining_days'] > 0:
            daily_average_needed = daily_status['remaining_budget'] / daily_status['remaining_days']
            if daily_average_needed > daily_status['daily_budget'] * 1.5:
                alerts.append({
                    'type': 'monthly_trend',
                    'message': f"📊 Atenção: Para atingir sua meta, precisa gastar apenas R$ {daily_average_needed:.2f}/dia",
                    'severity': 'medium'
                })
        
        return alerts
    
    def get_budget_alerts(self, user_id: int):
        """Alertas de orçamento por categoria"""
        budget_data = budget_service.get_budgets_with_status(user_id)
        alerts = []
        
        for alert_msg in budget_data['alerts']:
            alerts.append({
                'type': 'budget_alert',
                'message': alert_msg,
                'severity': 'high' if '🚨' in alert_msg else 'medium'
            })
        
        return alerts
    
    def get_economy_alerts(self, user_id: int, month: int = None, year: int = None):
        """Alertas de economia (método Breno)"""
        summary = self.finance_calc.get_monthly_summary(user_id, month, year)
        alerts = []
        
        if summary['economia_real_vs_meta'] < 0:
            alerts.append({
                'type': 'economy_alert',
                'message': f"🎯 ECONOMIA ABAIXO DA META! Está R$ {abs(summary['economia_real_vs_meta']):.2f} abaixo dos 25%",
                'severity': 'high'
            })
        elif summary['economia_real_vs_meta'] < summary['meta_economia'] * 0.1:
            alerts.append({
                'type': 'economy_warning',
                'message': f"💡 Faltam R$ {abs(summary['economia_real_vs_meta']):.2f} para atingir a meta de economia",
                'severity': 'medium'
            })
        
        return alerts
    
    def get_all_alerts(self, user_id: int, month: int = None, year: int = None):
        """Todos os alertas combinados"""
        alerts = []
        alerts.extend(self.get_daily_budget_alerts(user_id))
        alerts.extend(self.get_budget_alerts(user_id))
        alerts.extend(self.get_economy_alerts(user_id, month, year))
        
        # Ordenar por severidade (high primeiro)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order[x['severity']])
        
        return alerts[:6]  # Limitar a 6 alertas

# Instância global
alert_service = AlertService()