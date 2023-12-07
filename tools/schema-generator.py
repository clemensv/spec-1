import argparse
import copy
import json
import os
import re
from jsonpointer import resolve_pointer

avro_type_mapping = {
    "string": {"type": "string"},
    "object": {"type": "record"},
    "map": {"type": { "type": "map"}},
    "uri": {"type": "string"},
    "datetime": {"type": {"type":"int", "logicalType": "time-millis"}},
    "integer": {"type": "int"},
    "boolean": {"type": "boolean"},
    "array": {"type":{"type": "array", "items": ""}},
    "uritemplate": {"type": "string"},
    "binary": {"type": "bytes"},
}

json_type_mapping = {
    "string": {"type": "string"},
    "object": {"type": "object"},
    "map": {"type": "object"},
    "uri": {"type": "string", "format": "uri"},
    "datetime": {"type": "string", "format": "date-time"},
    "integer": {"type": "integer"},
    "boolean": {"type": "boolean"},
    "array": {"type": "array"},
    "uritemplate": {"type": "string", "format": "uri-template"},
    "binary": {"type": "string", "format": "base64"},
}

json_common_attributes = {
    "id": {"type": "string"},
    "name": {"type": "string"},
    "epoch": {"type": "integer"},
    "self": {"type": "string", "format": "uri"},
    "description": {"type": "string"},
    "documentation": {"type": "string", "format": "uri"},
    "labels": {"type": "object"},
    "format": {"type": "string"},
    "createdby": {"type": "string"},
    "createdon": {"type": "string", "format": "date-time"},
    "modifiedby": {"type": "string"},
    "modifiedon": {"type": "string", "format": "date-time"}
}

avro_common_attributes = [
    {"name": "id", "type": "string"},
    {"name": "name", "type": ["string", "null"]},
    {"name": "epoch", "type": ["int", "null"]},
    {"name": "self", "type": "string"},
    {"name": "description", "type": ["string", "null"]},
    {"name": "documentation", "type": ["string", "null"]},
    {"name": "labels", "type": { "type": "map", "values": ["string", "null"]}},
    {"name": "createdby", "type": ["string", "null"]},
    {"name": "createdon", "type": [{"type":"int", "logicalType": "time-millis"}, "null"]},
    {"name": "modifiedby", "type": ["string", "null"]},
    {"name": "modifiedon", "type": [{"type":"int", "logicalType": "time-millis"},"null"]}
]

avro_generic_record_name = "GenericRecord"
avro_generic_record = {
  "type": "record",
  "name": avro_generic_record_name,
  "fields": [
    {
      "name": "object",
      "type": {
        "type": "map",
        "values": [
          "null",
          "boolean",
          "int",
          "long",
          "float",
          "double",
          "bytes",
          "string",
          {
            "type": "array",
            "items": [
              "null",
              "boolean",
              "int",
              "long",
              "float",
              "double",
              "bytes",
              "string",
              avro_generic_record_name 
            ]
          },
          avro_generic_record_name
        ]
      }
    }
  ]
}



def pascal(string):
    if not string or len(string) == 0:
        return string
    words = []
    if '_' in string:
        # snake_case
        words = re.split(r'_', string)
    elif '-' in string:
        # dash-case
        words = re.split(r'-', string)
    elif string[0].isupper():
        # PascalCase
        words = re.findall(r'[A-Z][a-z0-9_]*\.?', string)
    else:
        # camelCase
        words = re.findall(r'[a-z]+\.?|[A-Z][a-z0-9_]*\.?', string)
    result = ''.join(word.capitalize() for word in words)
    return result

def camel(string):
    pascalString = pascal(string)
    return pascalString[0:1].lower() + pascalString[1:]


def generate_openapi(model_definition):

    # now recursively find all $ref attributes in the template and replace them with references to the appropriate schema
    def replace_refs(schema_fragment: dict, expression: str, reference: str):
        for k,v in schema_fragment.items():
            if k == "$ref":
                if v == expression:
                    schema_fragment[k] = reference
            if isinstance(v, dict):
                replace_refs(v, expression, reference)        
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        replace_refs(item, expression, reference)

    def replace_ops(schema_fragment: dict, expression: str, reference: str):
        for k,v in schema_fragment.items():
            if k == "operationId":
                if v.find(expression) != -1:
                    schema_fragment[k] = v.replace(expression, reference)
            if isinstance(v, dict):
                replace_ops(v, expression, reference)        
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        replace_ops(item, expression, reference)

    try:
        template_file_name = os.path.join(os.path.dirname(__file__), '..', 'core', 'templates', 'xregistry_openapi_template.json')
        with open(template_file_name) as file:
            openapi = json.load(file)
        json_schema = generate_json_schema(model_definition, True)
        # merge JSON schema with template
        for schema_name, schema in json_schema["components"]["schemas"].items():
            openapi["components"]["schemas"][schema_name] = schema
        # do the fixups 

        path = "/"
        root_template = openapi["paths"][path]
        replace_refs(root_template, "{%-documentTypeReference-%}", f"#/components/schemas/document")

        path = "/{%-groupNamePlural-%}"
        path_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            path_template_copy = copy.deepcopy(path_template)
            replace_refs(path_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")
            replace_ops(path_template_copy, "{%-groupNamePlural-%}", f"{pascal(group['plural'])}")
            openapi["paths"][f"/{group['plural']}"]: path_template_copy
        openapi["paths"].pop(path)

        path = "/{%-groupNamePlural-%}/{groupid}"
        group_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            group_template_copy = copy.deepcopy(group_template)
            replace_refs(group_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")
            replace_ops(group_template_copy, "{%-groupNameSingular-%}", f"{pascal(group['singular'])}")
            openapi["paths"][f"/{group['plural']}/{{groupid}}"] = group_template_copy
        
        openapi["paths"].pop(path)
        path = "/{%-groupNamePlural-%}/{groupid}/{%-resourceNamePlural-%}"
        resource_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            for _, resource in group.get("resources", {}).items():
                resource = resolve_resource(group, resource)
                resource_template_copy = copy.deepcopy(resource_template)
                replace_refs(resource_template_copy, "{%-resourceTypeReference-%}", f"#/components/schemas/{resource['singular']}")
                replace_refs(resource_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")        
                replace_ops(resource_template_copy, "{%-resourceNamePlural-%}", f"{pascal(group['singular'])}{pascal(resource['plural'])}")    
                openapi["paths"][f"/{group['plural']}/{{groupid}}/{resource['plural']}"]= resource_template_copy

        openapi["paths"].pop(path)
        path = "/{%-groupNamePlural-%}/{groupid}/{%-resourceNamePlural-%}/{resourceid}"
        resourceid_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            for _, resource in group.get("resources", {}).items():
                resource = resolve_resource(group, resource)
                resourceid_template_copy = copy.deepcopy(resourceid_template)
                replace_refs(resourceid_template_copy, "{%-resourceTypeReference-%}", f"#/components/schemas/{resource['singular']}")
                replace_refs(resourceid_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")
                replace_ops(resourceid_template_copy, "{%-resourceNameSingular-%}", f"{pascal(group['singular'])}{pascal(resource['singular'])}")
                openapi["paths"][f"/{group['plural']}/{{groupid}}/{resource['plural']}/{{resourceid}}"]= resourceid_template_copy

        openapi["paths"].pop(path)
        path = "/{%-groupNamePlural-%}/{groupid}/{%-resourceNamePlural-%}/{resourceid}/versions"
        versions_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            for _, resource in group.get("resources", {}).items():
                resource = resolve_resource(group, resource)
                versions_template_copy = copy.deepcopy(versions_template)
                replace_refs(versions_template_copy, "{%-resourceTypeReference-%}", f"#/components/schemas/{resource['singular']}")
                replace_refs(versions_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")
                replace_ops(versions_template_copy, "{%-resourceNameSingular-%}", f"{pascal(group['singular'])}{pascal(resource['singular'])}")
                openapi["paths"][f"/{group['plural']}/{{groupid}}/{resource['plural']}/{{resourceid}}/versions"]= versions_template_copy

        openapi["paths"].pop(path)
        path = "/{%-groupNamePlural-%}/{groupid}/{%-resourceNamePlural-%}/{resourceid}/versions/{versionid}"
        versionid_template = openapi["paths"][path]
        for _, group in model_definition.get("groups", {}).items():
            for _, resource in group.get("resources", {}).items():
                resource = resolve_resource(group, resource)
                versionid_template_copy = copy.deepcopy(versionid_template)
                replace_refs(versionid_template_copy, "{%-resourceTypeReference-%}", f"#/components/schemas/{resource['singular']}")
                replace_refs(versionid_template_copy, "{%-groupTypeReference-%}", f"#/components/schemas/{group['singular']}")
                replace_ops(versionid_template_copy, "{%-resourceNameSingular-%}", f"{pascal(group['singular'])}{pascal(resource['singular'])}")
                openapi["paths"][f"/{group['plural']}/{{groupid}}/{resource['plural']}/{{resourceid}}/versions/{{versionid}}"]= versionid_template_copy

        openapi["paths"].pop(path)
        return openapi
    except:
        print(f"Error opening template file {template_file_name}")
        raise


def generate_json_schema(model_definition, for_openapi=False) -> dict:
    """
    Generate a JSON schema for the given model definition.

    Args:
        model_definition (dict): The model definition to generate the schema for.
        for_openapi (bool, optional): Whether the schema is being generated for OpenAPI. Defaults to False.

    Returns:
        dict: The generated JSON schema.
    """
    
    def handle_item(resource_schema, type, item):
        if type == "object":
            resource_schema["type"] = "object"
            if "attributes" in item:
                handle_attributes(resource_schema,  item["attributes"])
        elif type == "map":
            resource_schema["type"] = "object"
            if "type" in item:
                resource_schema["additionalProperties"] = copy.deepcopy(json_type_mapping[item["type"]])
                if item["type"] == "object" or item["type"] == "map" or item["type"] == "array":
                    if "item" in item: 
                        handle_item(resource_schema["additionalProperties"], item["type"], item["item"])
        elif type == "array":
            resource_schema["type"] = "array"
            if "type" in item:
                resource_schema["items"] = copy.deepcopy(json_type_mapping[item["type"]])
                if item["type"] == "object" or item["type"] == "map" or item["type"] == "array":
                    if "item" in item: 
                        handle_item(resource_schema["items"], item["type"], item["item"])
        

    def handle_attributes(resource_schema, attributes):
        """
        This function takes in a resource schema and a dictionary of attributes and their properties.
        It iterates through each attribute and creates a JSON schema for it based on its properties.
        The function also handles nested attributes and conditional attributes using the "ifvalue" property.
        The resulting schema is added to the resource schema.
        """
        for attr_name, attr_props in attributes.items():
            attr_schema = copy.deepcopy(json_type_mapping[attr_props["type"]])
            
            if "description" in attr_props:
                attr_schema["description"] = attr_props["description"]
            
            if attr_props["type"] == "object" or attr_props["type"] == "map" or attr_props["type"] == "array":
                if "item" in attr_props:
                    handle_item(attr_schema, attr_props["type"], attr_props["item"])

            if "required" in attr_props and attr_props["required"] == True:
                if "required" not in resource_schema:
                    resource_schema["required"] = []
                resource_schema["required"].append(attr_name)
                            
            if "ifvalue" in attr_props:
                if attr_name == "*":
                    raise Exception("Can't use wild card attribute name with ifvalue")
                
                if for_openapi:
                    resource_schema["discriminator"] = {
                        "propertyName": attr_name,
                        "mapping": {}
                    }

                if attr_name in resource_schema["properties"]:
                    resource_schema["properties"].pop(attr_name)
                    if "required" in resource_schema and attr_name in resource_schema["required"]:
                        resource_schema["required"].remove(attr_name)

                one_of = []
                for condition_value, condition_props in attr_props["ifvalue"].items():
                    # create an identifier from condition_value, turning all spaces and special characters in to underscore
                    condition_schema_identifier = attr_name + "_" + "".join([c if c.isalnum() else "_" for c in condition_value])   
                    # for openapi, add a reference to this schema in the discriminator mapping         
                    if for_openapi:
                        resource_schema["discriminator"]["mapping"][condition_value] = f"#/components/schemas/{condition_schema_identifier}"

                    conditional_attr_schema = copy.deepcopy(attr_schema)
                    conditional_attr_schema.update({
                                "enum": [condition_value],
                            })
                    if "siblingattributes" in condition_props:
                        conditional_schema = {
                                    "properties": {
                                        attr_name: conditional_attr_schema
                                    },
                                    "required": [attr_name]
                                }
                        handle_attributes(conditional_schema,  condition_props.get("siblingattributes", {}))
                    else:
                        conditional_attr_schema.update({
                            "default": condition_value
                        })
                        conditional_schema = {
                            "properties": {
                                        attr_name: conditional_attr_schema
                                    },
                        }

                    if for_openapi:
                        resource_schema["discriminator"]["mapping"][condition_value] = f"#/components/schemas/{condition_schema_identifier}"
                        schema_definitions[condition_schema_identifier] = copy.deepcopy(conditional_schema)
                    else:
                        one_of.append(copy.deepcopy(conditional_schema))
                if len(one_of) > 0: 
                    if "oneOf" in resource_schema:
                        resource_schema["allOf"] = [{"oneOf" : resource_schema.pop("oneOf")}]
                        resource_schema["allOf"].append({"oneOf": one_of})
                    else:
                        resource_schema["oneOf"] = one_of
            else:
                if attr_name == "*":
                    if "additionalProperties" in resource_schema:
                        resource_schema["additionalProperties"].update(attr_schema)
                    else:
                        resource_schema["additionalProperties"] = copy.deepcopy(attr_schema)
                else:
                    if not "properties" in resource_schema:
                        resource_schema["properties"] = {}
                    resource_schema["properties"][attr_name] = copy.deepcopy(attr_schema)

    ## body of the core function starts here

    schema_group_names = []
    for k in model_definition.get("groups", {}).keys():
        schema_group_names.append(k.lower())
    
    if for_openapi:
        reference_prefix = "#/components/schemas/"
        schema = {
            "components": {
                "schemas": {
                    "document": {
                        "type": "object",
                        "properties": {},
                    }
                }
            }
        }
        document_properties = schema["components"]["schemas"]["document"]["properties"]
        schema_definitions = schema["components"]["schemas"]
    else:
        reference_prefix = "#/definitions/"
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://xregistry.io/schema/"+"-".join(schema_group_names),
            "properties": {},
            "definitions": {}
        }
        document_properties = schema["properties"]
        schema_definitions = schema["definitions"]    
    
    
    for _, group in model_definition.get("groups", {}).items():
        groups_name = group["plural"]
        group_name = group["singular"]
        groups_schema = {
            "type": "object",
            "additionalProperties": {"$ref": f"{reference_prefix}{group_name}"}
        }        

        document_properties[groups_name] = groups_schema
        resource_collection_properties = {}
        
        for _, resource in group.get("resources", {}).items():
            resource = resolve_resource(group, resource)            
            resource_name = resource["singular"]

            resource_schema = {
                "type": "object",
                "properties": copy.deepcopy(json_common_attributes),
                "required": ["id"],
            }

            attributes = resource.get("attributes", {})
            if resource.get("versions", 1) != 1:
                resource_version_schema = copy.deepcopy(resource_schema)
                handle_attributes(resource_version_schema, attributes)
                
                resource_schema["oneOf"] = [
                        {"required": ["versions"]},
                        {"required": ["versionsUrl", "versionsCount"]}
                    ]
                
                resource_schema["properties"].update(
                    {
                        "versionsUrl": {"type": "string"},
                        "versionsCount": {"type": "integer"},
                        "versions": {
                            "type": "object",
                            "additionalProperties": {
                                "$ref": f"{reference_prefix}{resource_name}Version"
                            }
                        }
                    })
                schema_definitions[f"{resource_name}Version"] = resource_version_schema
            else:
                handle_attributes(resource_schema, attributes)

            schema_definitions[resource_name] = resource_schema
            resource_collection_properties[resource["plural"]] = {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": f"{reference_prefix}{resource_name}",
                    }
                }
            

        group_schema = {
            "type": "object",
            "properties": copy.deepcopy(json_common_attributes),
            "required": ["id"],
        }
        attributes = group.get("attributes", {})
        handle_attributes(group_schema, attributes)
        for resource_collection_name, resource_collection_schema in resource_collection_properties.items():
            group_schema["properties"][resource_collection_name] = resource_collection_schema
        schema_definitions[group_name] = group_schema
    return schema



def generate_avro_schema(model_definition) -> dict:
    """
    Generates an Avro schema based on the given model definition.

    Args:
        model_definition (dict): The model definition to generate the schema from.

    Returns:
        dict: The generated Avro schema.
    """

    avro_generic_record_emitted = False
    record_types = set()

    def handle_item(resource_schema, type, item, name, prefix):
        if type == "object":
            if "attributes" in item:
                item_schema = { "type": "record", "name" : prefix+name+"Type", "fields": []}
                handle_attributes(item_schema, item["attributes"], prefix)
                resource_schema["type"] = item_schema
            else:
                if avro_generic_record_emitted:
                    resource_schema["type"] = avro_generic_record_name
                else:
                    resource_schema["type"] = copy.deepcopy(avro_generic_record)
                    avro_generic_record_emitted = True
        elif type == "map":
            resource_schema["type"] =  { "type": "map", "name": prefix+name+"Type","values": "" }
            if "type" in item:
                item_schema = copy.deepcopy(avro_type_mapping[item["type"]])
                if item["type"] == "object" or item["type"] == "map" or item["type"] == "array":
                    if "item" in item: 
                        handle_item(item_schema, item["type"], item["item"], name+"Item", prefix)                
                resource_schema["type"]["values"] = item_schema["type"]
            else:
                raise Exception("Map item must have a type specified")
        elif type == "array":
            resource_schema["type"] = { "type": "array", "name": prefix+name+"ArrayType", "items": "" }
            if "type" in item:
                item_schema = copy.deepcopy(avro_type_mapping[item["type"]])
                if item["type"] == "object" or item["type"] == "map" or item["type"] == "array":
                    if "item" in item: 
                        handle_item(item_schema, item["type"], item["item"], name, prefix)
                        resource_schema["type"]["items"] = item_schema["type"]
                else:
                    resource_schema["type"]["items"] = item_schema
            else:
                raise Exception("Array item must have a type specified")


    def handle_attributes(resource_schema, attributes, type_prefix=""):
        nonlocal avro_generic_record_emitted
        for attr_name, attr_props in attributes.items():
            pascal_attr_name=pascal(attr_name)
            # attribute schema is based on the type mapping
            attr_schema = copy.deepcopy(avro_type_mapping[attr_props["type"]])            
            if attr_name != "*":
                attr_schema["name"] = type_prefix+pascal_attr_name+"Type"
            # add the description, if any, as a doc attribute
            if "description" in attr_props:
                attr_schema["doc"] = attr_props["description"]
            
            if attr_props["type"] == "object" or attr_props["type"] == "map" or attr_props["type"] == "array":
                if "item" in attr_props:
                    handle_item(attr_schema, attr_props["type"], attr_props["item"], pascal_attr_name, type_prefix)
                else:
                    if attr_props["type"] == "object":
                        if avro_generic_record_emitted:
                            attr_schema["type"] = avro_generic_record_name
                        else:
                            attr_schema["type"] = copy.deepcopy(avro_generic_record)
                            avro_generic_record_emitted = True
                    else:
                        raise Exception("array or map attribute must have an item specified")

            if "ifvalue" in attr_props:
                if attr_name == "*":
                    raise Exception("Can't use wild card attribute name with ifvalue")
          
                if pascal_attr_name in resource_schema["fields"]:
                    resource_schema["fields"].pop(pascal_attr_name)

                union = []
                for condition_value, condition_props in attr_props["ifvalue"].items():
                    # create an identifier from condition_value, turning all spaces and special characters in to underscore
                    condition_schema_identifier = pascal_attr_name + pascal("".join([c if c.isalnum() else "_" for c in condition_value]))   
                    conditional_schema = {
                                "type": "record",
                                "name": type_prefix+condition_schema_identifier+"Type",
                                "fields": []
                            }
                    handle_attributes(conditional_schema,  condition_props.get("siblingattributes", {}), condition_schema_identifier)
                    union.append(conditional_schema)
                if len(union) > 0: 
                    field_schema = {
                            "name": camel(pascal_attr_name),
                             "type":  union
                    }
                    if "description" in attr_props:
                        field_schema["doc"] = attr_props["description"]
                    resource_schema["fields"].append(field_schema)
            else:
                if attr_name == "*":
                    if "name" in attr_schema["type"]:
                        attr_schema["type"]["name"] = type_prefix+pascal_attr_name+"ExtensionItemType"
                    field_schema = {
                            "name": "Extensions",
                            "type":  {
                               "type": "map",
                               "name": type_prefix+"ExtensionsType",
                               "default": {},
                               "values": attr_schema["type"]
                             }}
                    if "description" in attr_props:
                        field_schema["doc"] = attr_props["description"]
                    resource_schema["fields"].append(field_schema)
                else:
                    attr_schema["name"] = camel(pascal_attr_name)
                    # if the attribute is not required, union the type with null    
                    #if not "required" in attr_props or attr_props["required"] == False:
                    #    attr_schema = ["null", attr_schema]
                    resource_schema["fields"].append(attr_schema)
            


    ## body of the core function starts here
    document_type = {
        "type": "record",
        "name": "DocumentType",
        "namespace": "io.xregistry",
        "fields": [],
    }
    document_properties = document_type["fields"]

    for _, group in model_definition.get("groups", {}).items():
        groups_name = group["plural"]
        group_name = group["singular"]
        resource_collection_fields = []
        
        for _, resource in group.get("resources", {}).items():
            resource = resolve_resource(group, resource)            
            resource_name = resource["singular"]
            if resource_name in record_types:
                resource_collection_fields.append({
                    "name": camel(resource["plural"]),
                    "type" :{
                        "type": "map",
                        "values": pascal(resource_name)+"Type"
                    }
                    })
            else:
                record_types.add(resource_name)
                resource_schema = {
                    "type": "record",
                    "name": pascal(resource_name)+"Type",
                    "fields": copy.deepcopy(avro_common_attributes)
                }
                attributes = resource.get("attributes", {})
                if resource.get("versions", 1) != 1:
                    resource_version_schema = copy.deepcopy(resource_schema)
                    handle_attributes(resource_version_schema, attributes)
                    resource_version_schema["name"] = pascal(resource_name)+"VersionType"
                    resource_schema["fields"].append(
                        { 
                            "name": "versions", 
                            "type": [ 
                                {
                                    "type": "map",
                                    "values": resource_version_schema
                                },
                                {
                                    "type": "record",
                                    "name": pascal(resource_name)+"VersionInfo",
                                    "fields": [
                                        {
                                            "name": "versionsUrl",
                                            "type": "string"
                                        },
                                        {
                                            "name": "versionCount",
                                            "type": "int"
                                        }
                                    ]
                                }
                            ]
                        })
                else:
                    handle_attributes(resource_schema, attributes)

                resource_collection_fields.append({
                    "name": camel(resource["plural"]),
                    "type" :{
                        "type": "map",
                        "values": resource_schema
                    }
                })
           

        group_schema = {
            "type": "record",
            "name": pascal(group_name)+"Type",
            "fields": copy.deepcopy(avro_common_attributes),
        }
        attributes = group.get("attributes", {})
        handle_attributes(group_schema, attributes)
        for resource_collection in resource_collection_fields:
            group_schema["fields"].append(resource_collection)
        groups_schema = {
            "name": camel(groups_name),
            "type": {
                "type": "map",
                "values": group_schema
            }
        }        
        document_properties.append(groups_schema)

    return document_type


def resolve_resource(group, resource):
    if "uri" in resource:
        try:
            base_uri = group["$source"]
            file_uri = resource["uri"]

                    # split off the JSON pointer part, if any
            if "#" in file_uri:
                file_uri, json_pointer = file_uri.split("#", 1)
                    # find out if it is a http URL or a relative path
            if file_uri.lower().startswith('http'):
                        # it is a http URL, retrieve the file
                import requests
                response = requests.get(file_uri)
                resource_object = response.json()
            else:
                file_uri = file_uri.replace('/', os.sep)
                path = os.path.join(os.path.dirname(base_uri), file_uri)
                        # it is a file path, load the file 
                with open(path) as file:
                    resource_object = json.load(file)
            if json_pointer:
                resource = resolve_pointer(resource_object, json_pointer)
            else:
                resource = resource_object
        except:
            print(f"Error loading model definition from {file_uri}")
            raise
    return resource





# Replace this with your model definition
model_definition = {
    "schemas": ["json-schema/draft-07"],
    #... rest of your model definition
}

# read model definition from file ../schema/model.json
# make the path relative to this script file, irrespective of working directory

def main():
    parser = argparse.ArgumentParser(description='Generate JSON schema from model definition')
    parser.add_argument('--type', type=str, help='type of document to generate', choices=['json-schema', 'avro-schema', 'openapi'], default='json-schema')
    parser.add_argument('--output', type=str, help='Path for output file', default='', required=False)
    parser.add_argument('input_files', type=str, help='Path to input files', nargs='+')

    args = parser.parse_args()

    json_schema = None
    model_definition = { "groups": {} }
    for input_file in args.input_files:
        with open(input_file) as file:
            input_definition = json.load(file)
            if "groups" in input_definition:
                for group_name, group_definition in input_definition["groups"].items():
                    # convert file.name to using OS separators
                    file_name = file.name.replace('/', os.sep)
                    group_definition["$source"] = os.path.join(os.getcwd(),file_name)
                    if group_name not in model_definition["groups"]:
                        model_definition["groups"][group_name] = group_definition
                        

    if (args.type == 'json-schema'):
        json_schema = generate_json_schema(model_definition)
        if args.output:
            with open(args.output, 'w') as of:
                json.dump(json_schema, of, indent=2)
        else:
            print(json.dumps(json_schema, indent=2))
    elif (args.type == 'avro-schema'):
        avro_schema = generate_avro_schema(model_definition)
        if args.output:
            with open(args.output, 'w') as of:
                json.dump(avro_schema, of, indent=2)
        else:
            print(json.dumps(avro_schema, indent=2))
    elif (args.type == 'openapi'):  
        openapi = generate_openapi(model_definition)   
        if args.output:
            with open(args.output, 'w') as of:
                json.dump(openapi, of, indent=2)
        else:
            print(json.dumps(openapi, indent=2))


if __name__ == '__main__':
    main()
