import argparse
import json
import time
import httpx
from pydantic import ValidationError
from collector import (
    collect_metrics
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitoring agent for Windows and Linux")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Send one measurement and exit")
    mode.add_argument("--collect-only", action="store_true", help="Print one measurement without sending")
    args = parser.parse_args()

    try:
        from config import settings
        from client import (
            send_metrics
        )
    except ValidationError as error:
        fields = ", ".join(".".join(str(part) for part in item["loc"]) for item in error.errors())
        print(f"Ошибка настроек: проверь .env рядом с агентом. Поля: {fields}", flush=True)
        return 2

    while True:
        success = False
        try:
            metrics = collect_metrics(settings.service_names)
            if args.collect_only:
                print(json.dumps(metrics, indent=4, ensure_ascii=False), flush=True)
                return 0
            send_metrics(metrics)
            print("Метрики отправлены", flush=True)
            success = True
        except httpx.HTTPStatusError as error:
            print(f"Сервер отклонил запрос: {error.response.status_code}", flush=True)
        except httpx.RequestError:
            print("Метрики не были отправлены: ошибка соединения или таймаут", flush=True)
        except OSError:
            print("Ошибка при сборе метрик", flush=True)

        if args.once or args.collect_only:
            return 0 if success else 1
        time.sleep(settings.send_interval_seconds)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Агент остановлен")
