# Agentic Patch Management System

This document provides a detailed explanation of the inner workings of the Agentic Patch Management System. It covers the data flow, from mock data ingestion to the generation of the final patch plan, and explains the logic behind the decision-making processes.

## How it Works

The system is designed to automate the process of identifying, assessing, scheduling, and documenting security patches. It uses a series of agents, each responsible for a specific task, to create a comprehensive patch plan. The entire process is orchestrated by the `PatchPlanGenerator` class, which you can find in `orchestrator/patch_plan_generator.py`.

### Data Ingestion

The system starts by ingesting mock data to simulate a real-world scenario. This data is located in the `data/` directory and consists of two main components:

1.  **CVEs (Common Vulnerabilities and Exposures):** A list of mock CVEs is stored in `data/mock_cves.json`. Each CVE entry includes information such as the CVE ID, a description of the vulnerability, the affected software, and a base severity score.

2.  **Vendor Notes:** Fictional vendor notes are located in the `data/vendor_notes/` directory. These notes provide additional context and guidance from the software vendors regarding the patches. They can include details about the patch's priority, potential side effects, and recommended deployment procedures.

This data is read and processed by the `PatchPlannerAgent` at the beginning of the patch planning process.

### The Patching Pipeline

The `PatchPlanGenerator` coordinates a series of agents to create the final patch plan. Here's a step-by-step breakdown of the pipeline:

1.  **Patch Identification (`PatchPlannerAgent`):** The process begins with the `PatchPlannerAgent`, which reads the mock CVEs and vendor notes. It identifies the necessary patches and gathers the initial information for each one.

2.  **Information Retrieval (`RAGRetrieverAgent`):** The `RAGRetrieverAgent` (Retrieval-Augmented Generation) takes the vendor notes and indexes them into a ChromaDB vector store. This allows the system to perform semantic searches on the vendor documentation, enabling it to find the most relevant information for each patch.

3.  **Risk Assessment (`RiskAssessorAgent`):** The `RiskAssessorAgent` is responsible for determining the risk associated with each patch. It takes the information gathered so far and uses a set of predefined rules to calculate a risk score. The severity of a patch is determined by a combination of the base severity score from the CVE and the context provided in the vendor notes. For example, a patch for a critical vulnerability that is actively being exploited will be assigned a higher severity than a patch for a low-risk vulnerability.

    *   **LLM-Powered Risk Assessment (Optional):** The system has the capability to use a Large Language Model (LLM) to enhance the risk assessment process. When enabled, the `LLMReasoningAgent` is used to analyze the CVE data and vendor notes to provide a more nuanced and context-aware risk assessment. You can enable this feature by setting `use_llm=True` when instantiating the `PatchPlanGenerator` in `main.py`.

4.  **Patch Scheduling (`PatchSchedulerAgent`):** Once the risks have been assessed, the `PatchSchedulerAgent` creates a schedule for deploying the patches. It takes into account the severity of each patch, the availability of the target systems, and any dependencies between patches. The goal is to create a schedule that minimizes downtime and ensures that the most critical patches are deployed first.

5.  **Auditing and Compliance (`AuditorAgent`):** The `AuditorAgent` adds compliance and audit metadata to the patch plan. It identifies which compliance frameworks (e.g., PCI-DSS, HIPAA) are relevant to each patch and adds the necessary documentation to the plan. This ensures that the patching process is fully documented and compliant with all relevant regulations.

### Output Generation

After running the pipeline, the system generates a comprehensive patch plan in the form of a JSON file. This file is saved in the `data/` directory and contains all the information gathered and generated during the process, including:

*   A list of all the identified patches
*   The risk assessment for each patch
*   The deployment schedule
*   The compliance and audit metadata

This JSON file is the final output of the system and provides a complete and actionable plan for deploying the necessary security patches.

### Running the System

To run the system, simply execute the `main.py` file from one step above the backend folder:

```bash
python main.py
```

This will trigger the entire pipeline and generate the patch plan JSON file in the `data/` directory.
