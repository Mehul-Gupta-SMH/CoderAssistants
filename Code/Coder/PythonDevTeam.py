import os.path

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

from CoderAssistants.Code.Utlities import base_utils

# @base_utils.log_function
def generate_python_code(topic:str):

    config_list = [ {'model': base_utils.get_config_val(config_type="model_config",key_list=["OPEN_AI","model_name"]),
                     'api_key': base_utils.get_config_val(config_type="model_config",key_list=["OPEN_AI","api_key"])} ]


    team_members = base_utils.get_config_val(config_type="prompts",get_all=True,key_list = ["python_dev","team_members"])

    member_agents = {}

    for members in team_members:
        print("members :",members)
        member_agents[members] = AssistantAgent(name=members
                                    , system_message=team_members[members]['persona']
                                    , llm_config={"config_list": config_list}
                                    , description = team_members[members]['description']
                                    )

    groupchat = GroupChat(agents=list(member_agents.values())
                          # , admin_name= 'Technical Manager'
                          , messages=[]
                          , max_round=8
                          , allowed_or_disallowed_speaker_transitions = {
                            # "project_planner":["qa_validator","code_validator","code_writer","qa_developer"],
                            member_agents["project_planner"]:[
                                member_agents["code_validator"],
                                member_agents["qa_validator"]
                            ],
                            # "qa_developer":["code_validator","project_planner"],
                            member_agents["qa_developer"]:[
                                member_agents["code_validator"],
                                member_agents["project_planner"]
                            ],
                            # "code_writer":["qa_validator","project_planner"],
                            member_agents["code_writer"]:[
                                member_agents["qa_validator"],
                                member_agents["project_planner"]
                            ],
                            # "code_validator":["qa_developer","qa_validator","project_planner"],
                            member_agents["code_validator"]:[
                                member_agents["qa_developer"],
                                member_agents["qa_validator"],
                                member_agents["project_planner"]
                            ],
                            # "qa_validator":["code_writer","code_validator","project_planner"],
                            member_agents["qa_validator"]:[
                                member_agents["code_writer"],
                                member_agents["code_validator"],
                                member_agents["project_planner"]
                            ],
                            }
                          , speaker_transitions_type = "disallowed"
                          ,speaker_selection_method='auto')

    team_manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

    user_proxy = UserProxyAgent( "user_proxy",
                                 code_execution_config={"work_dir": "Code", "use_docker": False}
                                 )

    user_proxy.initiate_chat(team_manager,message=topic)

    ConvLog = r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Coder\ResultsConvLog"

    with open(os.path.join(ConvLog,topic[:25].replace(".","_")+".ConvLog"),"w+") as ConvResults:
        full_message = ""
        for message in groupchat.messages:
            message =  message['role'] + " ---> "+ message['name'] + "\n\n" +  message['content'] + "\n\n################\n\n"
            full_message += message
        ConvResults.write(full_message)


    if len(groupchat.messages[-1]['content'].strip()):
        return groupchat.messages[-1]['content']
    else:
        return groupchat.messages[-2]['content']
