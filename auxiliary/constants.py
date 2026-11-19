
card_data = {
        "Страна": "Россия",
        "ИНН": "7701234567",
        "Адрес": "г. Москва, ул. Примерная, д. 1, но это не точно ...",
    }

JOB_ID = 'check_mailing_statuses_job'

# Permissions для рассылок
CAN_VIEW_ALL_MAILINGS = 'mailing.can_view_all_mailings'
CAN_STOP_MAILING = 'mailing.can_stop_mailing'

# Permissions для клиентов
CAN_VIEW_ALL_CLIENTS = 'clients.can_view_all_clients'

# Permissions для пользователей
CAN_BLOCK_USER = 'users.can_block_user'
CAN_SEE_USERS = 'users.can_see_users'

# Время жизни токена подтверждения регистрации в часах
INTERVAL = 24
