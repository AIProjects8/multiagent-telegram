from AgentsCore.Questionnaire.questionnaire_item import QuestionnaireItem

class QuestionnaireState:
  
  def __init__(self):
    self.state: dict[str, list[QuestionnaireItem]] = {}

  def add_item(self, user_id: str, item: QuestionnaireItem):
    if user_id not in self.state:
      self.state[user_id] = []
    self.state[user_id].append(item)

  def get_item(self, user_id: str) -> list[QuestionnaireItem]:
    return self.state.get(user_id, [])

  def get_all_items(self) -> dict[str, list[QuestionnaireItem]]:
    return self.state