# 👤 **Logs com Identificação de Usuário - Exemplos Práticos**

## 🎯 **O que foi Implementado**

Agora **todos os logs mostram quem fez cada ação**! O sistema automaticamente:

1. **Extrai dados do token JWT** quando disponível
2. **Identifica o usuário** em cada requisição
3. **Propaga informações** através de toda a cadeia de logs
4. **Mantém contexto de segurança** para auditoria

---

## 📝 **Exemplos de Logs por Cenário**

### **1. 🔓 Usuário Anônimo (Sem Token)**

#### **Middleware - Requisição de Usuário Não Autenticado**
```json
{
  "timestamp": "2025-01-24T10:30:15.123Z",
  "level": "INFO",
  "service": "http_middleware",
  "correlation_id": "req_abc12345",
  "message": "Incoming request: POST /auth/login - User: Anonymous (192.168.1.100)",
  "operation": "http_request_start",
  "user_context": {
    "authenticated": false,
    "user_id": null,
    "email": null,
    "role": null,
    "display_name": "Anonymous",
    "client_ip": "192.168.1.100"
  }
}
```

### **2. 🔐 Usuário Autenticado (Com Token Válido)**

#### **Middleware - Usuário Logado Fazendo Requisição**
```json
{
  "timestamp": "2025-01-24T10:45:30.456Z",
  "level": "INFO",
  "service": "http_middleware",  
  "correlation_id": "req_def67890",
  "message": "Incoming request: GET /books/ - User: j***n@email.com (admin)",
  "operation": "http_request_start",
  "user_context": {
    "authenticated": true,
    "user_id": "123",
    "email": "john@email.com",
    "role": "admin",
    "display_name": "j***n@email.com (admin)",
    "jwt_valid": true,
    "token_exp": 1706097600,
    "client_ip": "192.168.1.100"
  }
}
```

#### **BookService - Busca Feita por Usuário Específico**
```json
{
  "timestamp": "2025-01-24T10:45:30.567Z",
  "level": "INFO",
  "service": "BookService",
  "correlation_id": "req_def67890",
  "message": "Operation search_books: completed (45ms)",
  "operation": "business_operation",
  "business_data": {
    "operation": "search_books",
    "result": "completed",
    "duration_ms": 45.67
  },
  "query_stats": {
    "title": "Python",
    "category": "Programming", 
    "results_found": 12
  }
}
```

### **3. ⚠️ Token Expirado**

#### **Middleware - Token Vencido**
```json
{
  "timestamp": "2025-01-24T11:00:15.789Z",
  "level": "WARNING",
  "service": "http_middleware",
  "correlation_id": "req_ghi11223",
  "message": "Incoming request: GET /books/ - User: Unauthenticated (Expired Token)",
  "operation": "http_request_start",
  "user_context": {
    "authenticated": false,
    "jwt_valid": false,
    "jwt_error": "token_expired",
    "display_name": "Expired Token",
    "client_ip": "192.168.1.100"
  }
}
```

### **4. 🔑 Eventos de Login**

#### **AuthService - Login Bem-sucedido com Contexto de Segurança**
```json
{
  "timestamp": "2025-01-24T10:30:15.200Z",
  "level": "INFO",
  "service": "AuthService",
  "correlation_id": "req_abc12345",
  "message": "Auth login: success for j***n@email.com",
  "operation": "auth_event",
  "auth_data": {
    "event": "login",
    "user_email": "j***n@email.com", 
    "success": true
  },
  "user_id": "123",
  "token_expires_at": "2025-01-24T12:30:15.000Z",
  "duration_ms": 185.43,
  "security_context": {
    "client_ip": "192.168.1.100",
    "session_type": "jwt_token",
    "token_lifetime_hours": 2,
    "user_role": "admin",
    "login_success": true
  }
}
```

#### **AuthService - Tentativa de Login Falhada (Segurança)**
```json
{
  "timestamp": "2025-01-24T10:35:22.456Z",
  "level": "WARNING", 
  "service": "AuthService",
  "correlation_id": "req_jkl33445",
  "message": "Auth login: failed for h***r@email.com",
  "operation": "auth_event",
  "auth_data": {
    "event": "login",
    "user_email": "h***r@email.com",
    "success": false
  },
  "error_reason": "invalid_password",
  "duration_ms": 123.45,
  "user_id": "456",
  "security_context": {
    "client_ip": "192.168.1.50",
    "threat_level": "medium",
    "attack_type": "brute_force_attempt",
    "existing_user": true
  }
}
```

### **5. 📚 Operações com Usuário Identificado**

#### **BookService - Busca Feita por Admin**
```json
{
  "timestamp": "2025-01-24T11:15:45.123Z",
  "level": "INFO",
  "service": "BookService", 
  "correlation_id": "req_mno55667",
  "message": "Starting book search: title=Python, category=Programming",
  "operation": "search_books_start",
  "query_params": {
    "title": "Python",
    "category": "Programming",
    "search_type": "title_and_category"
  },
  "current_user": {
    "user_id": "123",
    "email": "j***n@email.com",
    "role": "admin",
    "authenticated": true
  }
}
```

### **6. 🕸️ Scraping Executado por Admin**

#### **ScrapingService - Processo Iniciado por Usuário**
```json
{
  "timestamp": "2025-01-24T11:30:00.000Z",
  "level": "INFO",
  "service": "ScrapingService",
  "correlation_id": "req_pqr77889",
  "message": "Scraping process completed successfully",
  "operation": "scraping_complete",
  "final_stats": {
    "total_duration_ms": 45678.90,
    "books_scraped": 1000,
    "books_processed": 995,
    "books_saved": 987,
    "failed_processing": 5,
    "overall_success": true
  },
  "initiated_by": {
    "user_id": "123",
    "email": "j***n@email.com", 
    "role": "admin",
    "client_ip": "192.168.1.100"
  }
}
```

---

## 🔍 **Como Buscar nos Logs**

### **Por Usuário Específico**
```bash
# Todas as ações de um usuário específico
grep '"user_id":"123"' logs/*/2025-01-24.log

# Todas as ações de um email específico  
grep '"email":"john@email.com"' logs/*/2025-01-24.log
```

### **Por Tipo de Usuário** 
```bash
# Todas as ações de admins
grep '"role":"admin"' logs/*/2025-01-24.log

# Todas as ações de usuários anônimos
grep '"authenticated":false' logs/*/2025-01-24.log
```

### **Por IP (Detectar Ataques)**
```bash
# Atividades de um IP específico
grep '"client_ip":"192.168.1.50"' logs/*/2025-01-24.log

# Tentativas de login falhadas por IP
grep '"attack_type":"brute_force_attempt"' logs/*/2025-01-24.log
```

### **Auditoria de Segurança**
```bash
# Todos os logins bem-sucedidos
grep '"event":"login"' logs/AuthService/2025-01-24.log | grep '"success":true'

# Tentativas de acesso não autorizadas
grep '"threat_level":"medium\|high"' logs/*/2025-01-24.log

# Tokens expirados/inválidos
grep '"jwt_error"' logs/*/2025-01-24.log
```

---

## 🎯 **Benefícios Práticos**

### **🕵️ Auditoria Completa**
- **Quem** fez cada ação
- **Quando** a ação foi feita  
- **De onde** (IP) a ação veio
- **Com que permissões** (role)

### **🛡️ Segurança**
- Detecção de **tentativas de brute force**
- Monitoramento de **acessos suspeitos** 
- **Rastreamento de atividades** por usuário
- **Alertas automáticos** para padrões anômalos

### **🐛 Debugging**
- **Reproduzir problemas** específicos de usuário
- **Rastrear bugs** através do correlation ID
- **Contextualizar erros** com informações do usuário

### **📊 Analytics**
- **Padrões de uso** por tipo de usuário
- **Atividades mais comuns** por role
- **Performance** por segmento de usuário

---

## 🚀 **Como Testar**

### **1. Faça Login**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123"}'
```

### **2. Use o Token em Outras Requisições**
```bash
curl http://localhost:8000/books/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### **3. Veja os Logs**
```bash
# Console: vai mostrar "User: admin@admin.com (admin)" 
# Arquivos: terão contexto completo do usuário em JSON
tail -f logs/http_middleware/$(date +%Y-%m-%d).log
```

---

**🎉 Agora você sabe exatamente quem está fazendo o quê na sua API!** 

Cada log tem **identidade completa** do usuário, permitindo auditoria, segurança e debugging de nível enterprise! 🚀 