#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор Postman-коллекции для YooKassa API v3.

Собирает файл YooKassa-API.postman_collection.json из описания эндпоинтов ниже.
Запуск:  python3 build_collection.py

Документация API: https://yookassa.ru/developers/api
Быстрый старт:    https://yookassa.ru/developers/payment-acceptance/getting-started/quick-start
"""

import json
import os

SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
DOCS = "https://yookassa.ru/developers/api"
OUT = "YooKassa-API.postman_collection.json"

# ---------------------------------------------------------------------------
# Тела запросов (реальные примеры из документации YooKassa)
# ---------------------------------------------------------------------------

BODY_PAYMENT_CREATE = {
    "amount": {"value": "100.00", "currency": "RUB"},
    "capture": True,
    "confirmation": {
        "type": "redirect",
        "return_url": "https://www.example.com/return_url",
    },
    "description": "Заказ №37",
    "metadata": {"order_id": "37"},
}

BODY_PAYMENT_CAPTURE = {
    "amount": {"value": "100.00", "currency": "RUB"},
}

BODY_PAYMENT_CANCEL = {}

BODY_REFUND_CREATE = {
    "payment_id": "{{payment_id}}",
    "amount": {"value": "100.00", "currency": "RUB"},
    "description": "Возврат по заказу №37",
}

BODY_RECEIPT_CREATE = {
    "type": "refund",
    "payment_id": "{{payment_id}}",
    "send": True,
    "customer": {"email": "test@example.com"},
    "settlements": [
        {"type": "prepayment", "amount": {"value": "100.00", "currency": "RUB"}}
    ],
    "items": [
        {
            "description": "Товар",
            "quantity": "1.00",
            "amount": {"value": "100.00", "currency": "RUB"},
            "vat_code": 1,
            "payment_mode": "full_payment",
            "payment_subject": "commodity",
        }
    ],
}

BODY_PAYOUT_CREATE = {
    "amount": {"value": "320.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
    "description": "Выплата по заказу №37",
    "metadata": {"order_id": "37"},
}

BODY_DEAL_CREATE = {
    "type": "safe_deal",
    "fee_moment": "payment_succeeded",
    "description": "SafeDeal 37",
    "metadata": {"order_id": "37"},
}

BODY_INVOICE_CREATE = {
    "payment_data": {
        "amount": {"value": "250.00", "currency": "RUB"},
        "capture": True,
    },
    "cart": [
        {
            "description": "Товар",
            "price": {"value": "250.00", "currency": "RUB"},
            "quantity": "1",
        }
    ],
    "delivery_method_data": {"type": "self"},
    "expires_at": "{{invoice_expires_at}}",
    "description": "Счёт №37",
    "metadata": {"order_id": "37"},
}

BODY_PAYMENT_METHOD_CREATE = {
    "type": "bank_card",
    "confirmation": {
        "type": "redirect",
        "return_url": "https://www.example.com/return_url",
    },
    "card": {
        "number": "5555555555554444",
        "expiry_year": "2027",
        "expiry_month": "07",
        "csc": "123",
        "cardholder": "IVAN IVANOV",
    },
}

BODY_PERSONAL_DATA_CREATE = {
    "type": "payout_statement_recipient",
    "last_name": "Иванов",
    "first_name": "Иван",
    "middle_name": "Иванович",
    "birthdate": "2000-09-16",
    "metadata": {"order_id": "37"},
}

BODY_SELF_EMPLOYED_CREATE = {
    "itn": "643211730849",
    "confirmation": {"type": "redirect"},
    "description": "Самозанятый Иван",
}

BODY_WEBHOOK_CREATE = {
    "event": "payment.succeeded",
    "url": "https://www.example.com/notification_url",
}

# ---------------------------------------------------------------------------
# Описание эндпоинтов: (папка, [запросы])
# каждый запрос: name, method, path (список сегментов), query, body, desc
# ---------------------------------------------------------------------------

ENDPOINTS = [
    ("Платежи", [
        {
            "name": "Создать платёж",
            "method": "POST",
            "path": ["payments"],
            "body": BODY_PAYMENT_CREATE,
            "desc": "Создаёт объект платежа. `capture: true` — списание сразу, "
                    "`false` — двухстадийная оплата (холдирование). В ответе — "
                    "`confirmation.confirmation_url`, куда нужно перенаправить "
                    "покупателя. ID из ответа сохраняется в переменную `payment_id`.",
            "save_id": "payment_id",
        },
        {
            "name": "Список платежей",
            "method": "GET",
            "path": ["payments"],
            "query": [
                ("limit", "10"),
                ("status", "succeeded", True),
                ("created_at.gte", "2024-01-01T00:00:00.000Z", True),
                ("cursor", "", True),
            ],
            "desc": "Возвращает список платежей с фильтрацией и постраничной "
                    "навигацией (курсор `cursor` из поля `next_cursor`). "
                    "Фильтры: `status`, `payment_method`, `created_at.gte/gt/lte/lt`, "
                    "`captured_at.*`, `limit` (1–100).",
        },
        {
            "name": "Информация о платеже",
            "method": "GET",
            "path": ["payments", "{{payment_id}}"],
            "desc": "Возвращает данные о конкретном платеже по его идентификатору.",
        },
        {
            "name": "Подтвердить платёж (capture)",
            "method": "POST",
            "path": ["payments", "{{payment_id}}", "capture"],
            "body": BODY_PAYMENT_CAPTURE,
            "desc": "Списывает захолдированные средства для платежа в статусе "
                    "`waiting_for_capture`. Сумма может быть меньше или равна "
                    "изначальной. Тело можно оставить пустым `{}` для полного списания.",
        },
        {
            "name": "Отменить платёж (cancel)",
            "method": "POST",
            "path": ["payments", "{{payment_id}}", "cancel"],
            "body": BODY_PAYMENT_CANCEL,
            "desc": "Отменяет платёж в статусе `waiting_for_capture` и "
                    "разблокирует захолдированные средства.",
        },
    ]),
    ("Возвраты", [
        {
            "name": "Создать возврат",
            "method": "POST",
            "path": ["refunds"],
            "body": BODY_REFUND_CREATE,
            "desc": "Создаёт возврат по успешному платежу (`status: succeeded`). "
                    "Возможен частичный возврат. ID сохраняется в `refund_id`.",
            "save_id": "refund_id",
        },
        {
            "name": "Список возвратов",
            "method": "GET",
            "path": ["refunds"],
            "query": [
                ("limit", "10"),
                ("payment_id", "{{payment_id}}", True),
                ("status", "succeeded", True),
                ("cursor", "", True),
            ],
            "desc": "Список возвратов с фильтрами: `payment_id`, `status`, "
                    "`created_at.*`, `limit`, `cursor`.",
        },
        {
            "name": "Информация о возврате",
            "method": "GET",
            "path": ["refunds", "{{refund_id}}"],
            "desc": "Возвращает данные о конкретном возврате.",
        },
    ]),
    ("Чеки", [
        {
            "name": "Создать чек",
            "method": "POST",
            "path": ["receipts"],
            "body": BODY_RECEIPT_CREATE,
            "desc": "Формирует чек по 54-ФЗ (приход/возврат прихода). Используется "
                    "при раздельной передаче данных о платеже и чеке. "
                    "ID сохраняется в `receipt_id`.",
            "save_id": "receipt_id",
        },
        {
            "name": "Список чеков",
            "method": "GET",
            "path": ["receipts"],
            "query": [
                ("limit", "10"),
                ("payment_id", "{{payment_id}}", True),
                ("status", "succeeded", True),
                ("cursor", "", True),
            ],
            "desc": "Список чеков. Фильтры: `payment_id`, `refund_id`, `status`, "
                    "`created_at.*`, `limit`, `cursor`.",
        },
        {
            "name": "Информация о чеке",
            "method": "GET",
            "path": ["receipts", "{{receipt_id}}"],
            "desc": "Возвращает данные о конкретном чеке.",
        },
    ]),
    ("Счета (Invoices)", [
        {
            "name": "Создать счёт",
            "method": "POST",
            "path": ["invoices"],
            "body": BODY_INVOICE_CREATE,
            "desc": "Создаёт выставленный счёт на оплату. В ответе — ссылка на "
                    "оплату счёта. ID сохраняется в `invoice_id`.",
            "save_id": "invoice_id",
        },
        {
            "name": "Информация о счёте",
            "method": "GET",
            "path": ["invoices", "{{invoice_id}}"],
            "desc": "Возвращает данные о выставленном счёте.",
        },
    ]),
    ("Способы оплаты", [
        {
            "name": "Создать способ оплаты",
            "method": "POST",
            "path": ["payment_methods"],
            "body": BODY_PAYMENT_METHOD_CREATE,
            "desc": "Сохраняет способ оплаты (например, банковскую карту) для "
                    "последующих автоплатежей. ID сохраняется в `payment_method_id`.",
            "save_id": "payment_method_id",
        },
        {
            "name": "Информация о способе оплаты",
            "method": "GET",
            "path": ["payment_methods", "{{payment_method_id}}"],
            "desc": "Возвращает данные о сохранённом способе оплаты.",
        },
    ]),
    ("Выплаты", [
        {
            "name": "Создать выплату",
            "method": "POST",
            "path": ["payouts"],
            "body": BODY_PAYOUT_CREATE,
            "desc": "Создаёт выплату на банковскую карту, кошелёк ЮMoney или по СБП. "
                    "Требует подключённого сервиса выплат. ID сохраняется в `payout_id`.",
            "save_id": "payout_id",
        },
        {
            "name": "Информация о выплате",
            "method": "GET",
            "path": ["payouts", "{{payout_id}}"],
            "desc": "Возвращает данные о конкретной выплате.",
        },
    ]),
    ("Сделки (SafeDeal)", [
        {
            "name": "Создать сделку",
            "method": "POST",
            "path": ["deals"],
            "body": BODY_DEAL_CREATE,
            "desc": "Создаёт безопасную сделку для платформ и маркетплейсов. "
                    "ID сохраняется в `deal_id`.",
            "save_id": "deal_id",
        },
        {
            "name": "Список сделок",
            "method": "GET",
            "path": ["deals"],
            "query": [
                ("limit", "10"),
                ("status", "opened", True),
                ("cursor", "", True),
            ],
            "desc": "Список сделок. Фильтры: `status`, `created_at.*`, "
                    "`expires_at.*`, `limit`, `cursor`.",
        },
        {
            "name": "Информация о сделке",
            "method": "GET",
            "path": ["deals", "{{deal_id}}"],
            "desc": "Возвращает данные о конкретной сделке.",
        },
    ]),
    ("Персональные данные", [
        {
            "name": "Создать персональные данные",
            "method": "POST",
            "path": ["personal_data"],
            "body": BODY_PERSONAL_DATA_CREATE,
            "desc": "Передаёт персональные данные получателя выплаты для проверки. "
                    "ID сохраняется в `personal_data_id`.",
            "save_id": "personal_data_id",
        },
        {
            "name": "Информация о персональных данных",
            "method": "GET",
            "path": ["personal_data", "{{personal_data_id}}"],
            "desc": "Возвращает статус проверки персональных данных.",
        },
    ]),
    ("Самозанятые", [
        {
            "name": "Зарегистрировать самозанятого",
            "method": "POST",
            "path": ["self_employed"],
            "body": BODY_SELF_EMPLOYED_CREATE,
            "desc": "Регистрирует самозанятого для выплат. "
                    "ID сохраняется в `self_employed_id`.",
            "save_id": "self_employed_id",
        },
        {
            "name": "Информация о самозанятом",
            "method": "GET",
            "path": ["self_employed", "{{self_employed_id}}"],
            "desc": "Возвращает данные о зарегистрированном самозанятом.",
        },
    ]),
    ("Участники СБП", [
        {
            "name": "Список банков СБП",
            "method": "GET",
            "path": ["sbp_banks"],
            "desc": "Возвращает список банков — участников Системы быстрых платежей "
                    "(для выплат через СБП).",
        },
    ]),
    ("Магазин и вебхуки", [
        {
            "name": "Информация о магазине (me)",
            "method": "GET",
            "path": ["me"],
            "desc": "Возвращает информацию о магазине/шлюзе: `account_id`, статус, "
                    "включённые способы оплаты, тестовый режим.",
        },
        {
            "name": "Создать вебхук",
            "method": "POST",
            "path": ["webhooks"],
            "body": BODY_WEBHOOK_CREATE,
            "desc": "Подписывает приложение на уведомления о событиях "
                    "(`payment.succeeded`, `payment.canceled`, `refund.succeeded` и др.). "
                    "Доступно только при авторизации через OAuth-токен. "
                    "ID сохраняется в `webhook_id`.",
            "save_id": "webhook_id",
        },
        {
            "name": "Список вебхуков",
            "method": "GET",
            "path": ["webhooks"],
            "desc": "Возвращает список настроенных вебхуков приложения (OAuth).",
        },
        {
            "name": "Удалить вебхук",
            "method": "DELETE",
            "path": ["webhooks", "{{webhook_id}}"],
            "desc": "Удаляет вебхук по идентификатору (OAuth).",
        },
    ]),
]

# ---------------------------------------------------------------------------
# Скрипты (тесты) для запросов
# ---------------------------------------------------------------------------

def test_script(save_id=None):
    lines = [
        "pm.test(\"Статус-код 200\", function () {",
        "    pm.response.to.have.status(200);",
        "});",
        "",
        "pm.test(\"Ответ в формате JSON\", function () {",
        "    pm.response.to.be.json;",
        "});",
    ]
    if save_id:
        lines += [
            "",
            "var data = pm.response.json();",
            "if (data && data.id) {",
            f"    pm.collectionVariables.set(\"{save_id}\", data.id);",
            f"    console.log(\"Сохранён {save_id} = \" + data.id);",
            "}",
        ]
    return lines


# ---------------------------------------------------------------------------
# Сборка запроса
# ---------------------------------------------------------------------------

def build_request(ep):
    method = ep["method"]
    path = ep["path"]

    url = {
        "raw": "{{base_url}}/" + "/".join(path),
        "host": ["{{base_url}}"],
        "path": path,
    }

    query = ep.get("query")
    if query:
        q = []
        raw_pairs = []
        for item in query:
            key, val = item[0], item[1]
            disabled = len(item) > 2 and item[2]
            entry = {"key": key, "value": val}
            if disabled:
                entry["disabled"] = True
            q.append(entry)
            if not disabled:
                raw_pairs.append(f"{key}={val}")
        url["query"] = q
        if raw_pairs:
            url["raw"] += "?" + "&".join(raw_pairs)

    headers = []
    request = {
        "method": method,
        "header": headers,
        "url": url,
        "description": ep.get("desc", ""),
    }

    if "body" in ep:
        headers.append({"key": "Content-Type", "value": "application/json"})
        # Idempotence-Key обязателен для всех POST-запросов
        headers.append({"key": "Idempotence-Key", "value": "{{$guid}}"})
        request["body"] = {
            "mode": "raw",
            "raw": json.dumps(ep["body"], ensure_ascii=False, indent=2),
            "options": {"raw": {"language": "json"}},
        }

    item = {
        "name": ep["name"],
        "request": request,
        "response": [],
        "event": [
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "exec": test_script(ep.get("save_id")),
                },
            }
        ],
    }
    return item


def build_collection():
    items = []
    for folder_name, eps in ENDPOINTS:
        items.append({
            "name": folder_name,
            "item": [build_request(ep) for ep in eps],
        })

    collection = {
        "info": {
            "name": "YooKassa API v3",
            "description": (
                "Неофициальная Postman-коллекция для работы с API ЮKassa (YooKassa) v3.\n\n"
                f"Документация: {DOCS}\n\n"
                "## Настройка\n"
                "1. Импортируйте коллекцию в Postman.\n"
                "2. В переменных коллекции укажите `shop_id` (Идентификатор магазина) "
                "и `secret_key` (Секретный ключ) из личного кабинета ЮKassa.\n"
                "3. Авторизация (Basic) и заголовок `Idempotence-Key` подставляются "
                "автоматически.\n\n"
                "Тестовые данные для оплаты: карта 5555 5555 5555 4444, любой срок "
                "и CVC — платёж пройдёт в тестовом магазине."
            ),
            "schema": SCHEMA,
        },
        "auth": {
            "type": "basic",
            "basic": [
                {"key": "username", "value": "{{shop_id}}", "type": "string"},
                {"key": "password", "value": "{{secret_key}}", "type": "string"},
            ],
        },
        "event": [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": [
                        "// Идемпотентность: для POST-запросов заголовок Idempotence-Key",
                        "// задан значением {{$guid}} и генерируется при каждой отправке.",
                        "// Здесь при необходимости можно задать invoice_expires_at и т.п.",
                        "if (!pm.collectionVariables.get('invoice_expires_at')) {",
                        "    var d = new Date(Date.now() + 24*60*60*1000);",
                        "    pm.collectionVariables.set('invoice_expires_at', d.toISOString());",
                        "}",
                    ],
                },
            }
        ],
        "variable": [
            {"key": "base_url", "value": "https://api.yookassa.ru/v3", "type": "string"},
            {"key": "shop_id", "value": "", "type": "string"},
            {"key": "secret_key", "value": "", "type": "string"},
            {"key": "payment_id", "value": "", "type": "string"},
            {"key": "refund_id", "value": "", "type": "string"},
            {"key": "receipt_id", "value": "", "type": "string"},
            {"key": "invoice_id", "value": "", "type": "string"},
            {"key": "payment_method_id", "value": "", "type": "string"},
            {"key": "payout_id", "value": "", "type": "string"},
            {"key": "deal_id", "value": "", "type": "string"},
            {"key": "personal_data_id", "value": "", "type": "string"},
            {"key": "self_employed_id", "value": "", "type": "string"},
            {"key": "webhook_id", "value": "", "type": "string"},
            {"key": "invoice_expires_at", "value": "", "type": "string"},
        ],
        "item": items,
    }
    return collection


def main():
    collection = build_collection()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)

    n_folders = len(collection["item"])
    n_requests = sum(len(f["item"]) for f in collection["item"])
    size = os.path.getsize(OUT)
    print(f"Готово: {OUT}")
    print(f"Папок: {n_folders}, запросов: {n_requests}, размер: {size} байт")


if __name__ == "__main__":
    main()