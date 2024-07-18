# 🗂️🧠 Untangle

This project provides a command-line tool for organizing files, directories, and URLs. Using an advanced language model, it generates summary information, title and tags for each file, which makes it easier to search and filter them later.

## 🛠 Features

- **Add files, directories, or URLs**: Process and add metadata to the database.
- **Search**: Search files by keywords.
- **Filter**: Filter files by tags.
- **List**: List all files with optional date filtering.
- **Statistics**: Show various statistics about the stored files.
- **Tag Management**: Add and rename tags for files.
- **Export/Import**: Export and import the database.
- **Open**: Open a file by its ID.

## ⚙️ Configuration

Before running the program, ensure you have a `config.py` file with the following content:

```python
ollama_host = 'http://localhost:11434'
model_name = 'gemma2'
temperature_value = 0.12
attempts_number = 3
language = 'en' # only "en" and "ru" are available now
colors = {
    "header_text": "#cad3f5",
    "border": "#b7bdf8",
    "row_bg_1": "#24273a",
    "row_bg_2": "#1e2030",
    "id": "#939ab7",
    "title": "#cad3f5",
    "summary": "#939ab7",
    "file_type": "#939ab7",
    "path": "#cad3f5",
    "tags": "#939ab7"
}
```

## 🚀 Installation

1. **Clone the repository**:

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```
3. **Create venv**
    ```sh
    python3 -m venv .venv
    ```
4. **Create alias**
    ```sh
    alias un='<path to .venv/bin/python3> <path to app.py>'
    ```

## 📝 Usage

Run the program using:

```sh
python app.py <command> [options]
```

### Commands and Options

- **Add a file, directory, or URL**:
    ```sh
    python app.py add <input_path>
    ```

- **Search files by keywords**:
    ```sh
    python app.py search <keywords> [--format table|json|csv]
    ```

- **Filter files by tags**:
    ```sh
    python app.py filter --tags <tag1,tag2,...> [--format table|json|csv]
    ```

- **List all files**:
    ```sh
    python app.py list [--date-after YYYY-MM-DD] [--format table|json|csv]
    ```

- **Show statistics**:
    ```sh
    python app.py stats [--by-type] [--by-tag]
    ```

- **Manage tags**:
    - Add a tag to a file:
        ```sh
        python app.py tag add <file_id> <tag>
        ```
    - Rename a tag:
        ```sh
        python app.py tag rename <old_name> <new_name>
        ```

- **Export the database**:
    ```sh
    python app.py export
    ```

- **Import the database**:
    ```sh
    python app.py import
    ```

- **Open a file**:
    ```sh
    python app.py open <file_id>
    ```

## 📊 Example Outputs

### JSON Output

```json
[
  {
    "id": 1,
    "title": "Example File",
    "summary": "This is an example summary.",
    "file_type": "txt",
    "path": "/path/to/file.txt",
    "tags": ["example", "test"]
  }
]
```

### Table Output

```plaintext
ID    Title          Summary                     File Type    Path                   Tags
1     Example File   This is an example summary. txt          /path/to/file.txt      example, test
```

### CSV Output

```csv
id,title,summary,file_type,path,tags
1,Example File,This is an example summary.,txt,/path/to/file.txt,"example, test"
```

## 🎨 Customization

Modify the `config.py` to change the colors used in the table output.
