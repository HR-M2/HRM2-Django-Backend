"""
面试后评估的评估代理模块。
"""
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat
from typing import Dict, Any, List, Tuple, Callable
from .llm_config import get_llm_config
from .base import BaseAgentManager


def create_evaluation_agents(criteria: Dict[str, Any]) -> Tuple:
    """
    创建面试后评估代理。
    
    参数:
        criteria: 招聘条件字典
        
    返回:
        评估代理元组
    """
    llm_config = get_llm_config()
    
    # 1. 用户代理（招聘经理）
    user_proxy = UserProxyAgent(
        name="招聘负责人",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
        system_message="""你是企业招聘负责人，负责协调面试后评估流程。你的职责：
        1. 启动评估流程并提供所有候选人信息
        2. 确保专家按流程评审"""
    )
    
    # 2. 助手（评估协调员）
    assistant = AssistantAgent(
        name="评估协调员",
        llm_config=llm_config,
        system_message="""你是评估流程协调员。职责：
        1. 接收候选人资料并分发给各位专家
        2. 确保信息传递完整准确
        3. 协调评估流程顺利进行"""
    )
    
    # 3. HR专家
    min_experience = criteria.get('min_experience', 2)
    hr_agent = AssistantAgent(
        name="HR专家",
        llm_config=llm_config,
        system_message=f"""你是HR专家，负责综合素质评估。评估维度：
        1. 工作经验与岗位匹配度（重点关注{min_experience}年以上经验）
        2. 学历背景与证书资质
        3. 职业稳定性与发展潜力
        4. 人格特质分析：尽责性(可靠性)、宜人性(团队合作)、神经质(情绪稳定性)

        请对每位候选人：
        - 分析HR维度的适配性
        - 考虑人格测试结果和欺诈风险
        - 推荐1-2名候选人（实际招聘人数的1.5倍）
        - 给出具体推荐理由

        注意，你只能提出你的建议和想法，你不可以直接决定最终推荐

        输出格式：HR推荐：[候选人名单]，理由：[详细分析]"""
    )
    
    # 4. 技术专家
    required_skills = ', '.join(criteria.get('required_skills', []))
    technical_agent = AssistantAgent(
        name="技术专家",
        llm_config=llm_config,
        system_message=f"""你是技术专家，负责技术能力评估。技术标准：
        必备技能：{required_skills}

        评估重点：
        1. 技术栈匹配度和深度
        2. 项目经验的技术复杂度
        3. 问题解决能力和技术成长性
        4. 人格特质：开放性(创新能力)、尽责性(代码质量)

        请对每位候选人：
        - 分析技术能力与岗位匹配度
        - 评估技术描述的真实性（参考欺诈得分）
        - 推荐1-2名技术最合适的候选人
        - 提供技术层面的详细评价

        注意，你只能提出你的建议和想法，你不可以直接决定最终推荐

        输出格式：技术推荐：[候选人名单]，理由：[技术分析]"""
    )
    
    # 5. 项目经理专家
    manager_agent = AssistantAgent(
        name="项目经理专家",
        llm_config=llm_config,
        system_message="""你是项目管理专家，评估项目管理能力。关注点：
        1. 项目管理经验和成果
        2. 团队协作与沟通能力  
        3. 领导力与决策能力
        4. 人格特质：外倾性(沟通)、宜人性(合作)、神经质(抗压)

        请对每位候选人：
        - 分析项目管理能力匹配度
        - 评估项目经验真实性
        - 推荐1-2名项目管理最合适的候选人
        - 提供管理能力详细评价

        注意，你只能提出你的建议和想法，你不可以直接决定最终推荐

        输出格式：管理推荐：[候选人名单]，理由：[管理能力分析]"""
    )
    
    # 6. 评审专家（最终审查员）
    critic_agent = AssistantAgent(
        name="综合评审专家",
        llm_config=llm_config,
        system_message="""你是综合评审专家，职责：
        第一轮：
        1. 汇总三位专家的推荐名单
        2. 分析各候选人综合竞争力
        3. 提供初步招聘建议

        第二轮：
        1. 组织专家讨论确定最终人选
        2. 为每位候选人生成详细评估报告
        3. 提供招聘顺位排序推荐

        最终的评估报告输出要求：
        - 清晰的候选人对比分析（用表格呈现）
        - 人格特质对工作适应性评估
        - 欺诈风险提示
        - 具体的岗位适配性分析
        - 明确的招聘推荐顺位

        最终确认格式：招聘顺位推荐：[姓名1] > [姓名2] > [姓名3]
        所有流程确认结束后打印APPROVE代表对话结束"""
    )
    
    return user_proxy, assistant, hr_agent, technical_agent, manager_agent, critic_agent


class EvaluationAgentManager(BaseAgentManager):
    """面试后评估代理管理器。"""
    
    def __init__(self, criteria: Dict[str, Any]):
        super().__init__(criteria)
    
    def setup(self):
        """设置所有评估代理和群聊。"""
        agents = create_evaluation_agents(self.criteria)
        (self.user_proxy, self.assistant, self.hr_agent, 
         self.technical_agent, self.manager_agent, self.critic) = agents
        
        # 定义发言顺序
        speaker_sequence = [
            self.user_proxy,      # 0: 开始
            self.assistant,       # 1: 分发信息
            self.hr_agent,        # 2: HR评估
            self.technical_agent, # 3: 技术评估
            self.manager_agent,   # 4: 管理评估
            self.critic,          # 5: 第一轮总结
            self.critic,          # 6: 开始第二轮
            self.hr_agent,        # 7: HR深入讨论
            self.technical_agent, # 8: 技术深入讨论
            self.manager_agent,   # 9: 管理深入讨论
            self.critic           # 10: 最终总结
        ]
        
        def speaker_selector(last_speaker: autogen.Agent, groupchat: GroupChat):
            current_step = len(groupchat.messages)
            
            if current_step < len(speaker_sequence):
                next_speaker = speaker_sequence[current_step]
                self.speakers.append(next_speaker.name)
                self.update_task_speaker(next_speaker.name, current_step + 1)
                return next_speaker
            
            return None
        
        # 创建群聊
        self.create_group_chat(
            agents=list(agents),
            speaker_selector=speaker_selector,
            max_round=12
        )
        
        # 创建管理器
        self.create_manager()
    
    def run_evaluation(self, candidate_info: str, candidates_count: int) -> List[Dict]:
        """运行评估流程。"""
        position = self.criteria.get('position', '未知职位')
        required_skills = ', '.join(self.criteria.get('required_skills', []))
        min_experience = self.criteria.get('min_experience', 2)
        
        message = f"""## 面试后综合评估任务

### 评估背景
经过初筛和面试环节，现需要对候选人进行最终评估。

**招聘职位**：{position}
**需求人数**：1人
**核心要求**：{required_skills}，{min_experience}年以上经验

### 候选人信息
{candidates_count}位候选人已完成面试，具体信息如下：
{candidate_info}

### 评估流程
**第一轮：专家独立评估**
1. HR专家：综合素养、文化契合度、人格特质适配性
2. 技术专家：技术能力、项目经验、专业技能匹配度  
3. 项目经理专家：管理能力、团队协作、领导潜力
4. 每位专家推荐1-2名候选人（需求1.5倍）

**第二轮：综合讨论决策**
1. 综合评审专家汇总分析
2. 专家团队讨论确定最终人选
3. 生成详细评估报告和招聘顺位推荐

请按流程开始评估。"""
        
        return self.run_chat(self.user_proxy, message)
