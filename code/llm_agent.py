from openai import OpenAI
from typing import List, Dict

# define a base agent
class LLMAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url='http://10.15.88.73:5023/v1',
            api_key='ollama', 
        )

# define chat agent as a sub class
class LLMChatAgent(LLMAgent):
    def __init__(self):
        super().__init__()
        self.messages: List[Dict] = [
            {"role": "system", "content": (
                "主角：通过种果实、砍木材、摘苹果并进行售卖来获取金币。\n"
                "商人：你可以在商店购买种子和出售已有商品。\n"
                "捣蛋鬼：如果捣蛋鬼每追上你一次，你的金币就会少10个。"
            )}
        ]

    def send_message(self, user_message: str) -> str:
        """
        发送用户消息并获取助手回复。
        """
        self.messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model="llama3.2",
                messages=self.messages,
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_reply = "抱歉，发生了一个错误。"

        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

# define decision agent as a sub class
class LLMDecisionAgent(LLMAgent):
    def __init__(self):
        super().__init__()
        self.messages: List[Dict] = [
            {"role": "system", "content": 
            "根据我输出的数字，如果输入的数字是奇数，则输出1，如果输入的数字是偶数，输出2，只输出一个字符"
            }
        ]

    def decide(self, money: int) -> bool:
        self.messages.append({"role": "user", "content": str(money)})

        try:
            response = self.client.chat.completions.create(
                model="llama3.2",
                messages=self.messages,
            )
            assistant_reply = response.choices[0].message.content.strip()
            reply = int(assistant_reply)
        except Exception as e:
            print(f"Error during decision: {e}")
            return False

        self.messages.append({"role": "assistant", "content": assistant_reply})

        if reply == 1:
            raining = True
        else:
            raining = False
        return raining

print("LLMDecisionAgent loaded successfully")
