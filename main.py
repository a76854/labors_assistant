# ============================================================================
# main.py - 项目主入口和使用示例
# ============================================================================
# 这个文件演示如何使用法律 Agent 工作流
# 提供了多种使用方式和实际案例
# ============================================================================

from typing import Optional
from agent.workflow import (
    get_legal_agent_workflow,
    execute_legal_query,
    LegalAgentWorkflow,
)
from agent.state import AgentState
from langchain_core.messages import HumanMessage


# ============================================================================
# 【使用方式 1】最简洁的方式 - 直接调用函数
# ============================================================================
def example_1_quick_query():
    """
    最快速的方式：一行代码执行查询
    
    适合：简单调试、快速原型开发
    """
    print("\n" + "=" * 70)
    print("【示例 1】快速查询方式")
    print("=" * 70)
    
    # 直接执行查询
    result = execute_legal_query(
        user_query="公司拖欠我的工资3个月，共计15,000元，我该怎么办？",
        max_iterations=10,
        verbose=True
    )
    
    # 输出结果
    print("\n【最终答案】")
    print(result["final_answer"])
    
    print("\n【推理步骤】")
    for i, step in enumerate(result["reasoning_steps"], 1):
        print(f"  {i}. {step}")
    
    print("\n【使用工具】")
    for tool in result["tools_used"]:
        print(f"  - {tool}")


# ============================================================================
# 【使用方式 2】创建工作流对象 - 推荐方式
# ============================================================================
def example_2_workflow_object():
    """
    创建工作流对象，适合多次查询的场景
    
    适合：实际应用中的持续使用、多用户场景
    """
    print("\n" + "=" * 70)
    print("【示例 2】使用工作流对象")
    print("=" * 70)
    
    # 初始化工作流（在应用启动时做一次）
    workflow = get_legal_agent_workflow()
    
    # 执行第一个查询
    print("\n--- 查询 1: 合同纠纷 ---")
    result1 = workflow.run(
        user_query="我签了一份购买合同，卖家没有按时交货，该怎么办？",
        max_iterations=10,
        verbose=False
    )
    print(f"答案: {result1['final_answer'][:100]}...")
    
    # 执行第二个查询
    print("\n--- 查询 2: 侵权赔偿 ---")
    result2 = workflow.run(
        user_query="邻居的狗咬伤了我，导致医疗费用3000元，我能要求赔偿吗？",
        max_iterations=10,
        verbose=False
    )
    print(f"答案: {result2['final_answer'][:100]}...")


# ============================================================================
# 【使用方式 3】流式执行 - 实时看到推理过程
# ============================================================================
def example_3_streaming():
    """
    使用流式执行，实时看到 Agent 的思考过程
    
    适合：Web 应用中的实时反馈、日志查看
    """
    print("\n" + "=" * 70)
    print("【示例 3】流式执行（实时推理过程）")
    print("=" * 70)
    
    workflow = get_legal_agent_workflow()
    
    print("\nAgent 正在推理，请稍候...\n")
    
    # 流式执行查询
    for event in workflow.stream(
        user_query="我的著作权被侵犯了，有人未经授权发表了我的小说，我该怎么办？",
        max_iterations=10
    ):
        # 这里可以逐步接收和处理推理过程中的事件
        # 可以实时更新 UI 或日志
        print(f"[事件] {event}")


# ============================================================================
# 【使用方式 4】手动构建和自定义
# ============================================================================
def example_4_custom_workflow():
    """
    更细粒度的控制：手动创建状态、自定义配置
    
    适合：需要深度定制、集成到复杂系统
    """
    print("\n" + "=" * 70)
    print("【示例 4】自定义工作流")
    print("=" * 70)
    
    # 手动创建工作流
    workflow = LegalAgentWorkflow()
    
    # 可以对大模型进行更细致的配置
    # 比如调整 temperature、max_tokens 等
    print("工作流已创建，您可以进行自定义配置")
    
    # 执行查询
    result = workflow.run(
        user_query="劳动合同到期了，公司说不续签，我有补偿吗？",
        max_iterations=10,
        verbose=True
    )
    
    print("\n【完整结果】")
    print(f"最终答案: {result.get('final_answer')}")
    print(f"已生成文书: {bool(result.get('generated_document'))}")
    print(f"推理轮数: {len(result.get('reasoning_steps', []))}")


# ============================================================================
# 【实际案例】真实的法律咨询场景
# ============================================================================
def example_5_real_case_contract_dispute():
    """
    真实案例：合同违约纠纷
    
    背景：客户与供应商签订了购销合同，供应商违约
    """
    print("\n" + "=" * 70)
    print("【案例 1】合同违约纠纷咨询")
    print("=" * 70)
    
    query = """
    我是一家贸易公司的采购经理。我们公司与供应商签订了一份买卖合同：
    - 合同金额：500,000 元
    - 交货期限：2024年2月28日
    - 产品：工业用母料
    - 产品规格和质量标准已在合同附件中详细列明
    
    但是供应商直到现在（2024年4月）还没有交货，我们多次催促也没有结果。
    因为没有及时拿到原料，我们的生产线已经停工一个月，
    损失了大约200,000元的订单利润。
    
    请问：
    1. 供应商这种行为违反了什么法律规定？
    2. 我们可以要求赔偿哪些费用？应该赔偿多少？
    3. 如果要起诉供应商，该怎么办？
    """
    
    workflow = get_legal_agent_workflow()
    result = workflow.run(user_query=query, max_iterations=15, verbose=True)
    
    print("\n【律师分析意见】")
    print(result["final_answer"])
    
    print("\n【建议后续步骤】")
    print("1. 保存所有往来的合同、邮件、聊天记录作为证据")
    print("2. 发送律师函，明确要求供应商在规定时间内履行义务")
    print("3. 如果供应商继续违约，可以向人民法院提起诉讼")
    print("4. 建议咨询专业律师制定详细的诉讼方案")


def example_6_real_case_labor_dispute():
    """
    真实案例：劳动纠纷
    
    背景：员工因非法解除被降薪或开除
    """
    print("\n" + "=" * 70)
    print("【案例 2】非法解除劳动合同咨询")
    print("=" * 70)
    
    query = """
    我在一家电子产品制造公司工作了5年，月薪18,000元。
    因为在内部微信群里发表了对公司管理的批评意见，
    公司突然以"违反公司纪律"的名义单方面解除了我的劳动合同，
    没有任何预警，也没有给我经济补偿。
    
    我觉得这个处理不合理，想请问：
    1. 公司的做法是否合法？
    2. 如果不合法，我应该获得什么样的赔偿？
    3. 我应该向那个部门投诉或起诉？
    """
    
    workflow = get_legal_agent_workflow()
    result = workflow.run(user_query=query, max_iterations=15, verbose=False)
    
    print("\n【法律分析】")
    print(result["final_answer"])
    
    print("\n【建议行动】")
    print("1. 立即收集证据（解除通知书、工资条、聊天记录等）")
    print("2. 在自解除之日起 30 天内向劳动仲裁委提出申请")
    print("3. 准备仲裁庭的答辩意见和证人证言")
    print("4. 建议聘请劳动领域的专业律师代理")


# ============================================================================
# 【主程序】
# ============================================================================
def main():
    """
    主程序：演示所有的使用方式和实际案例
    """
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "欢迎使用法律 AI Agent 系统" + " " * 19 + "║")
    print("║" + " " * 12 + "基于 LangGraph 和大模型的 ReAct 工作流" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # 选择要运行的示例
    examples = {
        "1": ("快速查询", example_1_quick_query),
        "2": ("工作流对象", example_2_workflow_object),
        "3": ("流式执行", example_3_streaming),
        "4": ("自定义工作流", example_4_custom_workflow),
        "5": ("案例：合同纠纷", example_5_real_case_contract_dispute),
        "6": ("案例：劳动纠纷", example_6_real_case_labor_dispute),
        "0": ("运行所有示例", None),
    }
    
    print("\n可用的示例：")
    for key, (name, _) in examples.items():
        if key != "0":
            print(f"  {key}. {name}")
    print("  0. 运行所有示例")
    print("  q. 退出")
    
    choice = input("\n请选择要运行的示例 (0-6, q): ").strip()
    
    if choice == "q":
        print("再见！")
        return
    
    if choice == "0":
        # 运行所有示例
        try:
            example_1_quick_query()
            example_2_workflow_object()
            # example_3_streaming()  # 可选：流式输出会很冗长
            example_4_custom_workflow()
            example_5_real_case_contract_dispute()
            example_6_real_case_labor_dispute()
        except Exception as e:
            print(f"\n执行出错：{str(e)}")
            print("提示：请确保已安装所有依赖包 (pip install -r requirements.txt)")
    
    elif choice in examples and choice != "0":
        _, func = examples[choice]
        if func:
            try:
                func()
            except Exception as e:
                print(f"\n执行出错：{str(e)}")
                print("提示：请确保已安装所有依赖包 (pip install -r requirements.txt)")
    
    else:
        print("无效的选择")


# ============================================================================
# 【快速测试】可以直接运行的最小示例
# ============================================================================
def quick_test():
    """
    最小化的测试，验证系统是否正确安装
    """
    print("\n【快速测试】执行一个简单的查询...\n")
    
    try:
        result = execute_legal_query(
            "房东要涨房租，合法吗？",
            max_iterations=5,
            verbose=False
        )
        print("✓ 系统工作正常！")
        print(f"\nAgent 回复: {result['final_answer'][:150]}...")
        
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        print("\n请检查：")
        print("1. 是否已安装所有依赖包？")
        print("   pip install -r requirements.txt")
        print("2. 是否配置了 OpenAI API Key？")
        print("   export OPENAI_API_KEY='你的 API Key'")


if __name__ == "__main__":
    # 取消下面注释以运行快速测试
    # quick_test()
    
    # 运行交互式菜单
    main()
