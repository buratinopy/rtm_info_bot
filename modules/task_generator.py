import logging

logger = logging.getLogger('rtm.task_generator')


class TaskGenerator:
    rule_name: str = None  # имя правила (должно быть уникальным)
    scheduler_params: dict = None  # как запускать таску
    connector_id: str = None  # id коннектора
    connector_config: str = None  # ссылка на файл конфига

    @staticmethod
    def format_rule_name(rule_name: str):
        rule_name = rule_name.replace(" ", "-")
        rule_name = rule_name.lower()
        return rule_name

    def generate_task(self, rule: dict):
        """
        Из правила формируем таску, которую с которой уже может работать коннектор
        rule_name переводится в нижний регистр и пробелы заменяются на "-"
        :param rule:
        :return: dict
        """
        self.rule_name = self.format_rule_name(rule['rule_name'])
        self.connector_id = rule['connector_id']
        self.scheduler_params = rule['scheduler_params']
        self.connector_params = rule['connector_params']
        gtask = {}
        for ik, iv in self.__dict__.items():
            if "__" in ik:
                continue
            gtask[ik] = iv
        return gtask
