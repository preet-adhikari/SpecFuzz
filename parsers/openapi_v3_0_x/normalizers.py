def normalize_schema(processed_spec: dict) -> dict:

    if not isinstance(processed_spec, (dict, list)):
        return processed_spec

    # First we identify nodes
    # List
    elif isinstance(processed_spec, list):
        for item in processed_spec:
            normalize_schema(item)

    # Dictionary
    if isinstance(processed_spec, dict):

        for key, value in processed_spec.items():
            processed_spec[key] = normalize_schema(value)

        if "allOf" in processed_spec:
            inherited_properties = {}
            existing_required = processed_spec.get("required", [])
            target_normalized_required = set(existing_required)

            for sub_schema in processed_spec["allOf"]:
                if "properties" in sub_schema:
                    inherited_properties.update(sub_schema["properties"])
                if "required" in sub_schema:
                    target_normalized_required.update(sub_schema["required"])

            # Finally
            inherited_properties.update(processed_spec.get("properties", ""))
            processed_spec["properties"] = inherited_properties
            processed_spec["required"] = sorted(list(target_normalized_required))
            processed_spec["type"] = "object"
            del processed_spec["allOf"]
    return processed_spec
