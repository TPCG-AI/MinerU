# Copyright (c) Opendatalab. All rights reserved.
import os
import time

from loguru import logger

from .custom_logits_processors import enable_custom_logits_processors
from .model_output_to_middle_json import result_to_middle_json
from ...data.data_reader_writer import DataWriter
from mineru.utils.pdf_image_tools import load_images_from_pdf
from ...utils.config_reader import get_device

from ...utils.enum_class import ImageType
from ...utils.model_utils import get_vram
from ...utils.models_download_utils import auto_download_and_get_model_root_path

from mineru_vl_utils import MinerUClient
from packaging import version


def get_language_aware_prompts(lang: str = "en") -> dict[str, str]:
    """Generate language-aware prompts based on the specified language."""
    # Map common language codes to full names
    lang_names = {
        "en": "English",
        "ch": "Chinese",
        "korean": "Korean",
        "japan": "Japanese",
        "ko": "Korean",
        "ja": "Japanese",
        "zh": "Chinese",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ar": "Arabic",
    }

    lang_name = lang_names.get(lang.lower(), "English")

    return {
        "table": f"\nTable Recognition (Output in {lang_name}):",
        "equation": f"\nFormula Recognition:",
        "[default]": f"\nText Recognition (Output in {lang_name}):",
        "[layout]": f"\nLayout Detection:",
    }


def get_language_aware_system_prompt(lang: str = "en") -> str:
    """Generate language-aware system prompt."""
    lang_names = {
        "en": "English",
        "ch": "Chinese",
        "korean": "Korean",
        "japan": "Japanese",
        "ko": "Korean",
        "ja": "Japanese",
        "zh": "Chinese",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ar": "Arabic",
    }

    lang_name = lang_names.get(lang.lower(), "English")

    return f"You are a helpful assistant specialized in document analysis. When recognizing text, output in {lang_name} language."


class ModelSingleton:
    _instance = None
    _models = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(
        self,
        backend: str,
        model_path: str | None,
        server_url: str | None,
        lang: str = "en",
        **kwargs,
    ) -> MinerUClient:
        # Include lang in cache key to create separate model instances per language
        key = (backend, model_path, server_url, lang)
        if key not in self._models:
            start_time = time.time()
            model = None
            processor = None
            vllm_llm = None
            vllm_async_llm = None
            batch_size = 0
            if backend in ['transformers', 'vllm-engine', "vllm-async-engine"] and not model_path:
                model_path = auto_download_and_get_model_root_path("/","vlm")
                if backend == "transformers":
                    try:
                        from transformers import (
                            AutoProcessor,
                            Qwen2VLForConditionalGeneration,
                        )
                        from transformers import __version__ as transformers_version
                    except ImportError:
                        raise ImportError("Please install transformers to use the transformers backend.")

                    if version.parse(transformers_version) >= version.parse("4.56.0"):
                        dtype_key = "dtype"
                    else:
                        dtype_key = "torch_dtype"
                    device = get_device()
                    model = Qwen2VLForConditionalGeneration.from_pretrained(
                        model_path,
                        device_map={"": device},
                        **{dtype_key: "auto"},  # type: ignore
                    )
                    processor = AutoProcessor.from_pretrained(
                        model_path,
                        use_fast=True,
                    )
                    try:
                        vram = get_vram(device)
                        if vram is not None:
                            gpu_memory = int(os.getenv('MINERU_VIRTUAL_VRAM_SIZE', round(vram)))
                            if gpu_memory >= 16:
                                batch_size = 8
                            elif gpu_memory >= 8:
                                batch_size = 4
                            else:
                                batch_size = 1
                            logger.info(f'gpu_memory: {gpu_memory} GB, batch_size: {batch_size}')
                        else:
                            # Default batch_ratio when VRAM can't be determined
                            batch_size = 1
                            logger.info(f'Could not determine GPU memory, using default batch_ratio: {batch_size}')
                    except Exception as e:
                        logger.warning(f'Error determining VRAM: {e}, using default batch_ratio: 1')
                        batch_size = 1
                elif backend == "vllm-engine":
                    try:
                        import vllm
                        from mineru_vl_utils import MinerULogitsProcessor
                    except ImportError:
                        raise ImportError("Please install vllm to use the vllm-engine backend.")
                    if "gpu_memory_utilization" not in kwargs:
                        kwargs["gpu_memory_utilization"] = 0.5
                    if "model" not in kwargs:
                        kwargs["model"] = model_path
                    if enable_custom_logits_processors() and ("logits_processors" not in kwargs):
                        kwargs["logits_processors"] = [MinerULogitsProcessor]
                    # 使用kwargs为 vllm初始化参数
                    vllm_llm = vllm.LLM(**kwargs)
                elif backend == "vllm-async-engine":
                    try:
                        from vllm.engine.arg_utils import AsyncEngineArgs
                        from vllm.v1.engine.async_llm import AsyncLLM
                        from mineru_vl_utils import MinerULogitsProcessor
                    except ImportError:
                        raise ImportError("Please install vllm to use the vllm-async-engine backend.")
                    if "gpu_memory_utilization" not in kwargs:
                        kwargs["gpu_memory_utilization"] = 0.5
                    if "model" not in kwargs:
                        kwargs["model"] = model_path
                    if enable_custom_logits_processors() and ("logits_processors" not in kwargs):
                        kwargs["logits_processors"] = [MinerULogitsProcessor]
                    # 使用kwargs为 vllm初始化参数
                    vllm_async_llm = AsyncLLM.from_engine_args(AsyncEngineArgs(**kwargs))

            # Generate language-aware prompts and system prompt
            custom_prompts = get_language_aware_prompts(lang)
            custom_system_prompt = get_language_aware_system_prompt(lang)

            self._models[key] = MinerUClient(
                backend=backend,
                model=model,
                processor=processor,
                vllm_llm=vllm_llm,
                vllm_async_llm=vllm_async_llm,
                server_url=server_url,
                batch_size=batch_size,
                prompts=custom_prompts,
                system_prompt=custom_system_prompt,
            )
            elapsed = round(time.time() - start_time, 2)
            logger.info(f"get {backend} predictor cost: {elapsed}s, lang: {lang}")
        return self._models[key]


def doc_analyze(
    pdf_bytes,
    image_writer: DataWriter | None,
    predictor: MinerUClient | None = None,
    backend="transformers",
    model_path: str | None = None,
    server_url: str | None = None,
    lang: str = "en",
    **kwargs,
):
    if predictor is None:
        predictor = ModelSingleton().get_model(backend, model_path, server_url, lang=lang, **kwargs)

    # load_images_start = time.time()
    images_list, pdf_doc = load_images_from_pdf(pdf_bytes, image_type=ImageType.PIL)
    images_pil_list = [image_dict["img_pil"] for image_dict in images_list]
    # load_images_time = round(time.time() - load_images_start, 2)
    # logger.info(f"load images cost: {load_images_time}, speed: {round(len(images_base64_list)/load_images_time, 3)} images/s")

    # infer_start = time.time()
    results = predictor.batch_two_step_extract(images=images_pil_list)
    # infer_time = round(time.time() - infer_start, 2)
    # logger.info(f"infer finished, cost: {infer_time}, speed: {round(len(results)/infer_time, 3)} page/s")

    middle_json = result_to_middle_json(results, images_list, pdf_doc, image_writer, lang=lang)
    return middle_json, results


async def aio_doc_analyze(
    pdf_bytes,
    image_writer: DataWriter | None,
    predictor: MinerUClient | None = None,
    backend="transformers",
    model_path: str | None = None,
    server_url: str | None = None,
    lang: str = "en",
    **kwargs,
):
    if predictor is None:
        predictor = ModelSingleton().get_model(backend, model_path, server_url, lang=lang, **kwargs)

    # load_images_start = time.time()
    images_list, pdf_doc = load_images_from_pdf(pdf_bytes, image_type=ImageType.PIL)
    images_pil_list = [image_dict["img_pil"] for image_dict in images_list]
    # load_images_time = round(time.time() - load_images_start, 2)
    # logger.info(f"load images cost: {load_images_time}, speed: {round(len(images_base64_list)/load_images_time, 3)} images/s")

    # infer_start = time.time()
    results = await predictor.aio_batch_two_step_extract(images=images_pil_list)
    # infer_time = round(time.time() - infer_start, 2)
    # logger.info(f"infer finished, cost: {infer_time}, speed: {round(len(results)/infer_time, 3)} page/s")
    middle_json = result_to_middle_json(results, images_list, pdf_doc, image_writer, lang=lang)
    return middle_json, results
