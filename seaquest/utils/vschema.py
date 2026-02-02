VALIDATION_SCHEMA = {
    "config_file": {
        "type": "string", 
        "required": True
    },
    "md_dir": {
        "type": "string", 
        "required": True
    },
    "data_file": {
        "type": "string",
        "required": True
    },
    "model_name": {
        "type": "string", 
        "required": True
    },
    "model_fun": {
        "type": "string", 
        "required": True
    },
    "prefix": {
        "type": "string", 
        "required": True
    },
    "log_file": {
        "type": "string"
    },
    "job_spec": {
        "type": "dict",
        "schema": {
            "resources": {
                "type": "dict", 
                "schema": {
                    "limits": {
                        "type": "dict",
                        "schema": {
                            "memory": {"type": "string", "required": True},
                            "cpu": {"type": "integer", "required": True},
                            "nvidia.com/gpu": {"type": "integer"},
                        }
                    },
                    "requests": {
                        "type": "dict",
                        "schema": {
                            "memory": {"type": "string", "required": True},
                            "cpu": {"type": "integer", "required": True},
                            "nvidia.com/gpu": {"type": "integer"},
                        }
                    },
                }
            },
            "graphics-card": {
                "type": "string",
            },
        }
    },
    "kube_env": {
        "type": "dict",
        "schema": {
            "namespace": {
                "type": "string", 
                "required": True
            },
        }
    },
    "pvc_params": {
        "type": "dict",
        "schema": {
            "pvc-name": {
                "type": "string"
            }
        }
    },
    "model_keyword_args": {
        "type": "dict",
    }
}