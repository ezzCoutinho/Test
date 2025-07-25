import os
import json
import uuid
import base64

OPA_TO_TALKTOME_TYPE = {
    "init": "start",
    "perg": "input-string",
    "pesquisa-satisfacao": "rating",
    "msg": "send-text",
    "tag": "tag",
    "cond": "switch",
    "eflow": "flow",
    "abrirAtendimentoWhatsapp": "send-text",
    "autenticacaoSimples": "input-text",
    "auto_vinculo": "script",
    "conta": "input-string",
    "delay": "delay",
    "desvioLigacao": "end",
    "enviarNotificacao": "alert",
    "integracaoErp": "script",
    "interactiveTemplate": "send-template",
    "transferirAtendimento": "team",
}


def generate_card_id():
    return uuid.uuid4().hex[:6]


def generate_option_id():
    return uuid.uuid4().hex[:5]


def generate_card(opa_type, block):
    talk_type = OPA_TO_TALKTOME_TYPE.get(opa_type, "undefined")
    card_id = generate_card_id()

    base_card = {
        "id": card_id,
        "nodeId": None,
        "type": talk_type,
        "content": {
            "title": "",
            "version": "1.0",
            "disabled": False,
            "timeout": False,
            "timeout_type": "minutes",
            "timeout_value": None,
            "max_retry": False,
            "max_retry_value": 3,
        },
    }

    if talk_type == "send-text":
        messages = block.get("mensagens", [{"value": f"Mensagem do tipo {opa_type}"}])
        base_card["content"]["message"] = messages[0]["value"]

    elif talk_type == "switch":
        conditional_value = block.get("valor_condicional")
        condition_value = ""
        if conditional_value:
            try:
                decoded_variable = base64.b64decode(conditional_value).decode("utf-8")
                parts = decoded_variable.split("|")
                variable = parts[0]
                if len(parts) > 1:
                    condition_value = parts[1]
            except:
                pass

        option_yes_id = generate_option_id()
        option_no_id = generate_option_id()

        base_card["content"].update(
            {
                "output": None,
                "title": "",
                "options": [
                    {
                        "id": option_yes_id,
                        "value": condition_value,
                        "filter_type": "string",
                        "operator": "eq",
                    },
                    {
                        "id": option_no_id,
                        "value": "NAO",
                        "filter_type": "string",
                        "operator": "eq",
                    },
                ],
                "message": None,
                "version": "1.0",
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "minutes",
                "timeout_value": None,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": None,
                "value": f"{{{{{variable}}}}}",
            }
        )

    elif talk_type == "input-menu":
        choice_options = block.get("opcoes_escolha", ["Opção 1", "Opção 2"])
        base_card["content"].update(
            {
                "message": block.get("pergunta", "Escolha uma opção:"),
                "options_type": "button",
                "invalid_message": "Opção inválida!",
                "options": [
                    {
                        "id": generate_card_id(),
                        "label": option,
                        "description": None,
                        "type": "QUICK_REPLY",
                        "url": None,
                    }
                    for option in choice_options
                ],
            }
        )

    elif talk_type == "tag":
        action = block.get("action", "append")
        base_card["content"].update(
            {
                "output": None,
                "title": "",
                "options": None,
                "message": block.get("message"),
                "time_group": None,
                "except_time_group": None,
                "timeout_message": None,
                "card_id": None,
                "action": action,
                "tags": [block.get("nome_etiqueta")],
            }
        )

    elif talk_type == "input-string":
        question = block.get("pergunta")
        variable = block.get("variavel")
        base_card["content"].update(
            {
                "output": variable,
                "title": "",
                "options": None,
                "message": question,
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "seconds",
                "timeout_value": None,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": None,
                "validate": False,
                "validation_type": "string",
                "invalid_message": "",
                "regular_expression": "",
            }
        )

    elif talk_type == "rating":
        evaluation_question = block.get("pergunta")
        base_card["content"].update(
            {
                "output": "",
                "title": "",
                "options": [
                    {
                        "id": "1",
                        "label": "Bom",
                        "description": "3",
                        "type": "QUICK_REPLY",
                        "url": None,
                    },
                    {
                        "id": "2",
                        "label": "Neutro",
                        "description": "2",
                        "type": "QUICK_REPLY",
                        "url": None,
                    },
                    {
                        "id": "3",
                        "label": "Ruim",
                        "description": "1",
                        "type": "QUICK_REPLY",
                        "url": None,
                    },
                ],
                "message": evaluation_question,
                "version": "1.0",
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "minutes",
                "timeout_value": 15,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": None,
                "invalid_message": "",
                "required_comment": False,
                "comment_message": None,
            }
        )

    elif talk_type == "delay":
        delay_time = block.get("tempo_delay")
        if delay_time == "0.25":
            delay_time = 15
            delay_type = "seconds"
        elif delay_time == "0.5":
            delay_time = 30
            delay_type = "seconds"
        else:
            delay_time = block.get("tempo_delay")
            delay_type = "minutes"
        base_card["content"].update(
            {
                "output": None,
                "title": "",
                "options": None,
                "message": block.get("message"),
                "time_group": None,
                "except_time_group": None,
                "timeout_message": None,
                "delay_value": delay_time,
                "delay_type": delay_type,
                "card_id": None,
                "tags": [],
            }
        )

    elif talk_type == "script":
        script = block.get("opcao")
        if script == "desbloqueioConfianca":
            script = '# Importa a classe IXC do módulo de plugins para comunicação com a API do IXC\nfrom plugins import IXC\n\n# Cria uma instância do IXC para realizar chamadas à API\nixc = IXC()\n\n# Obtém o ID do contrato a partir do contexto do workflow\ncontract_id = workflow[\'CONTRACT_ID\']\n\n# Monta o corpo (payload) da requisição com o ID do contrato\npayload = {\n    "id": contract_id\n}\n\n# Realiza uma chamada POST para o endpoint de desbloqueio por confiança\nresponse = ixc.call_api(\n    method="POST",                                  # Método HTTP: POST\n    path="/webservice/v1/desbloqueio_confianca",    # Endpoint para realizar o desbloqueio\n    payload=payload,                                # Dados enviados no corpo da requisição\n    timeout=120                                     # Tempo máximo de espera da resposta (em segundos)\n)\n\n# Retorna a resposta da API com o resultado da operação\nreturn response\n'
        else:
            script = None
        base_card["content"].update(
            {
                "output": "",
                "title": "",
                "options": None,
                "message": None,
                "version": "1.0",
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "minutes",
                "timeout_value": None,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": None,
                "code": script,
                "continue_on_error": False,
            }
        )

    elif talk_type == "flow":
        base_card["content"].update(
            {
                "output": "",
                "title": "",
                "options": None,
                "message": None,
                "version": "1.0",
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "minutes",
                "timeout_value": None,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": "",
                "flow_id": "",
                "continue": False,
            }
        )

    elif talk_type == "condition":
        variable = (
            block.get("variableName")
            or block.get("opcao_condicional_valor")
            or "{{variavel}}"
        )
        base_card["content"].update(
            {
                "output": "",
                "title": "",
                "options": [
                    {
                        "id": "7p72t7",
                        "value": "Sim",
                        "filter_type": "string",
                        "operator": "eq",
                    },
                    {
                        "id": "fnvlc",
                        "value": "Não",
                        "filter_type": "string",
                        "operator": "eq",
                    },
                ],
                "message": None,
                "version": "1.0",
                "time_group": None,
                "except_time_group": None,
                "disabled": False,
                "timeout": False,
                "timeout_message": None,
                "timeout_type": "minutes",
                "timeout_value": None,
                "max_retry": False,
                "max_retry_value": 10,
                "card_id": None,
                "value": variable,
            }
        )

    elif talk_type == "input-text":
        base_card["content"]["message"] = block.get(
            "textoPedirCpfCnpj", "Digite seu CPF/CNPJ:"
        )

    elif talk_type == "alert":
        base_card["content"]["message"] = block.get(
            "mensagemNotificacao", "Nova notificação"
        )

    elif talk_type == "flow":
        base_card["content"]["message"] = (
            f"Executar fluxo: {block.get('eflow_nome', '')}"
        )

    elif talk_type == "team":
        base_card["content"]["message"] = (
            f"Transferir para: {block.get('transf_dep_nome') or block.get('transf_user_nome')}"
        )

    else:
        base_card["content"]["message"] = (
            f"[AVISO] Tipo '{opa_type}' não mapeado corretamente."
        )

    return base_card


def convert_opa_to_talktome(opa_data):
    structure = json.loads(opa_data["estrutura"])
    nodes = []
    edges = []
    id_map = {}
    switch_option_ids = {}

    nodes.append(
        {
            "id": "start",
            "type": "start",
            "position": {"x": -34.5, "y": -6.5},
            "data": {"title": "", "cards": [], "webhook": None},
        }
    )

    first_valid_node_id = None

    for index, block in enumerate(structure):
        block_type = block.get("type", "undefined")
        if block_type == "init":
            continue

        block_id = generate_card_id()
        id_map[index] = block_id

        if first_valid_node_id is None:
            first_valid_node_id = block_id

        position = {
            "x": block.get("position", {}).get("left", 0),
            "y": block.get("position", {}).get("top", 0),
        }

        card = generate_card(block_type, block)

        node = {
            "id": block_id,
            "type": "stack",
            "position": position,
            "data": {"title": f"{block_type}", "cards": [card], "webhook": None},
        }

        if block_type == "cond":
            options = card["content"].get("options", [])
            if len(options) >= 2:
                switch_option_ids[block_id] = [options[0]["id"], options[1]["id"]]

        nodes.append(node)

    if first_valid_node_id:
        edges.append(
            {
                "id": f"edge-start-{first_valid_node_id}",
                "source": "start",
                "target": first_valid_node_id,
                "sourceHandle": None,
                "targetHandle": None,
                "className": None,
                "animated": False,
            }
        )

    for index, block in enumerate(structure):
        block_type = block.get("type", "undefined")
        if block_type == "init":
            continue

        block_id = id_map[index]

        for next_key in ["next", "next1"]:
            if next_key in block:
                try:
                    target_index = int(block[next_key])
                    target_id = id_map.get(target_index)
                    if target_id:
                        source_handle = None
                        if block_type == "cond" and block_id in switch_option_ids:
                            if next_key == "next1":
                                source_handle = f"opt-{switch_option_ids[block_id][0]}"
                            elif next_key == "next":
                                source_handle = f"opt-{switch_option_ids[block_id][1]}"
                        edges.append(
                            {
                                "id": f"edge-{block_id}-{target_id}",
                                "source": block_id,
                                "target": target_id,
                                "sourceHandle": source_handle,
                                "targetHandle": None,
                                "className": None,
                                "animated": False,
                            }
                        )
                except:
                    continue

    return {"nodes": nodes, "edges": edges, "tags": []}


def process_flows(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith(".json"):
            file_path = os.path.join(input_folder, file)
            with open(file_path, "r", encoding="utf-8") as f:
                opa_data = json.load(f)

            converted = convert_opa_to_talktome(opa_data)

            output_path = os.path.join(output_folder, file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(converted, f, indent=2, ensure_ascii=False)

            print(f"✔ Convertido: {file}")


# Update paths if necessary
input_folder = "/Users/lucasafonso/fluxos-opa-suite/cliente-teste"
output_folder = "/Users/lucasafonso/fluxos-opa-suite/cliente-teste/convertidos"
process_flows(input_folder, output_folder)
