# header

A Python script that automatically prepends license/copyright headers to source files. Configuration is handled via a `.env` file, and each header is generated with the correct file name and an auto-generated description based on the file's path and context.

---

## Features

- Reads author, company, year, and target extensions from a `.env` file
- Inserts the actual **filename** into each header automatically
- **Auto-generates a description** based on the file name and its directory context (components, stores, services, utils, etc.)
- Supports any file extension — not limited to `.ts` / `.vue`
- Skips files that already have a header
- Configurable directory exclusions (e.g. `node_modules`, `.git`, `dist`)
- Works on a single file or an entire directory tree

---

## Project Structure

```
header/
├── header.py        # Main script
├── header.json      # Header templates with {{PLACEHOLDERS}}
├── .env             # Your local configuration (not committed)
└── .env.example     # Template to copy from
```

---

## Setup

1. **Clone the repository**

```bash
git clone https://github.com/AlexandreDFM/header.git
cd header/header
```

2. **Create your `.env` file**

```bash
cp .env.example .env
```

3. **Edit `.env`** with your details:

```env
HEADER_AUTHOR=John Doe
HEADER_COMPANY=Tux Inc.
HEADER_YEAR=                        # Leave empty to use the current year
HEADER_EXTENSIONS=.ts,.vue          # Comma-separated list of extensions
HEADER_EXCLUDE_DIRS=node_modules,.git,dist,build
```

---

## Usage

```bash
python3 header.py <path>
```

| Argument | Description                              |
|----------|------------------------------------------|
| `<path>` | A file or directory to process           |
| `-h`     | Show the help message                    |

### Examples

Add headers to all matching files in a project:

```bash
python3 header.py /path/to/my-project/src
```

Add a header to a single file:

```bash
python3 header.py /path/to/my-project/src/components/MyButton.vue
```

---

## How It Works

### Placeholder substitution

`header.json` contains two templates (`header` for `.ts` files and `vueHeader` for `.vue` files) using the following placeholders:

| Placeholder       | Resolved to                                      |
|-------------------|--------------------------------------------------|
| `{{FILE_NAME}}`   | The basename of the file (e.g. `MyButton.vue`)   |
| `{{AUTHOR}}`      | `HEADER_AUTHOR` from `.env`                      |
| `{{COMPANY}}`     | `HEADER_COMPANY` from `.env`                     |
| `{{YEAR}}`        | `HEADER_YEAR` from `.env`, or the current year   |
| `{{DESCRIPTION}}` | Auto-generated from the file name and path       |

### Description generation

The script analyses the file path to produce a meaningful description:

| Path pattern       | Example output                                     |
|--------------------|----------------------------------------------------|
| `components/`      | `Vue component for My Button.`                     |
| `views/`           | `Vue view component for User Profile page.`        |
| `stores/`          | `Pinia/Vuex store module for Auth.`                |
| `services/`        | `Service layer handling Api Client operations.`    |
| `utils/`           | `Utility functions for Date Formatter.`            |
| `types/`           | `TypeScript type definitions for User.`            |
| `index.ts`         | `Entry point for the <parent folder> module.`      |
| `main.ts` / `app.` | `Application entry point.`                         |
| *(fallback)*       | `TypeScript module for <name>.`                    |

### Generated header example

```ts
/*
File Name: userStore.ts
Author: John Doe
Creation Date: 2026
Description: Pinia/Vuex store module for User Store.

Copyright (c) 2026 Tux Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
...
*/
```

---

## Requirements

- Python 3.9+
- No third-party dependencies

---

## License

MIT License — see [LICENSE](LICENSE) for details.

