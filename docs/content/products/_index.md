---
title: "Our Products"
description: "Explore InfoTech.io's open-source educational technology products"
date: 2025-09-23
weight: 20
---

# Our Products

InfoTech.io develops a comprehensive ecosystem of open-source educational technology products designed to make IT learning accessible, interactive, and effective.

## 🎓 INFOTEKA - Interactive Learning Platform

**The flagship educational platform providing comprehensive IT courses with hands-on practice.**

### Features
- **Interactive Learning**: Courses combine theory with practical exercises and quizzes
- **Modular Architecture**: Each course is an independent module with its own progression
- **Real-time Feedback**: Immediate assessment through integrated Quiz Engine
- **Mobile-Friendly**: Responsive design for learning on any device
- **Progress Tracking**: Local storage-based progress without required registration

### Available Courses
- **[Linux Basics](https://linux-base.infotecha.ru)** - Complete beginner course
- **[Advanced Linux](https://linux-advanced.infotecha.ru)** - System administration
- **[Linux Professional](https://linux-professional.infotecha.ru)** - Expert-level content

### Technical Stack
- **Frontend**: Hugo Static Site Generator, JavaScript, CSS
- **Content**: Markdown with YAML frontmatter
- **Testing**: Quiz Engine integration
- **Deployment**: Automated CI/CD via GitHub Actions

### Links
- **Platform**: [infotecha.ru](https://infotecha.ru)
- **Source Code**: [github.com/info-tech-io/infotecha](https://github.com/info-tech-io/infotecha)
- **Content Repositories**: [github.com/info-tech-io](https://github.com/info-tech-io) (mod_* repositories)

---

## 🧪 Quiz Engine - Interactive Testing System

**A powerful, flexible system for creating and managing interactive quizzes and assessments.**

### Features
- **Multiple Question Types**: Multiple choice, true/false, fill-in-the-blank
- **Real-time Scoring**: Immediate feedback and detailed explanations
- **JSON Configuration**: Easy quiz creation and management
- **Embeddable**: Seamless integration with any web platform
- **Analytics**: Track completion rates and performance metrics
- **Customizable**: Flexible theming and styling options

### Use Cases
- Educational course assessments
- Employee training and certification
- Knowledge retention testing
- Interactive content engagement

### Technical Details
- **Language**: Pure JavaScript (ES6+)
- **Dependencies**: Zero external dependencies
- **Size**: Lightweight (~15KB minified)
- **Browser Support**: All modern browsers
- **Integration**: Simple HTML embed

### Example Quiz Configuration
```json
{
  "title": "Linux Basics Quiz",
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What command lists files in a directory?",
      "options": ["ls", "cd", "pwd", "mkdir"],
      "correct": 0,
      "explanation": "The 'ls' command lists the contents of a directory."
    }
  ]
}
```

### Links
- **Documentation**: [quiz.info-tech.io](https://quiz.info-tech.io)
- **Source Code**: [github.com/info-tech-io/quiz](https://github.com/info-tech-io/quiz)
- **Live Demo**: [quiz.info-tech.io/demo](https://quiz.info-tech.io/demo)

---

## 🏗️ Hugo Templates Factory - Site Generation Framework

**A flexible, modular framework for rapid creation of Hugo-based static sites with various templates and themes.**

### Features
- **Multiple Templates**: Educational, Corporate, Documentation, Blog templates
- **Theme System**: Interchangeable themes (Compose, Minimal, Custom)
- **Component Library**: Reusable components (Quiz Engine, Search, Navigation)
- **JSON Schema Validation**: Automated configuration validation
- **CLI Tools**: Command-line interface for site generation
- **CI/CD Integration**: Seamless GitHub Actions workflows

### Available Templates

#### Educational Template
- Optimized for course content and learning materials
- Integrated Quiz Engine support
- Progress tracking and navigation
- Student-friendly design

#### Corporate Template
- Professional business website layout
- Team pages, service descriptions
- Contact forms and call-to-action sections
- SEO optimized

#### Documentation Template
- Technical documentation focused
- API reference support
- Code syntax highlighting
- Search functionality

### Configuration Example
```json
{
  "name": "my-educational-site",
  "version": "1.0.0",
  "type": "educational",
  "build": {
    "template": "educational",
    "theme": "compose",
    "components": ["quiz-engine", "progress-tracker"]
  },
  "site": {
    "title": "My Course Platform",
    "description": "Learn programming with interactive courses",
    "baseURL": "https://mycourses.example.com"
  }
}
```

### Links
- **Documentation**: [hugo.info-tech.io](https://hugo.info-tech.io)
- **Source Code**: [github.com/info-tech-io/hugo-templates](https://github.com/info-tech-io/hugo-templates)
- **Template Gallery**: [hugo.info-tech.io/templates](https://hugo.info-tech.io/templates)

---

## 💻 Web Terminal - Browser-Based Interactive Terminal

**A secure, containerized terminal environment accessible through web browsers for hands-on learning.**

### Features
- **Docker-Based**: Isolated, secure container environments
- **Multiple Shells**: Bash, Zsh, Fish support
- **File System Access**: Full Linux environment with persistent storage
- **Real-time Collaboration**: Shared terminal sessions for pair programming
- **WebSocket Communication**: Low-latency, real-time terminal interaction
- **Security**: Sandboxed environments with configurable restrictions

### Use Cases
- Interactive programming tutorials
- Linux system administration training
- Code compilation and testing
- Remote development environments
- Educational labs and workshops

### Technical Architecture
- **Backend**: Node.js with Docker integration
- **Frontend**: Xterm.js terminal emulator
- **Communication**: WebSocket for real-time interaction
- **Container Management**: Docker Compose orchestration
- **Security**: Isolated containers with resource limits

### Integration
```javascript
// Embed Web Terminal in your educational content
const terminal = new WebTerminal({
  container: '#terminal-container',
  endpoint: 'wss://terminal.info-tech.io/session',
  environment: 'ubuntu-dev',
  user: 'student'
});
```

### Links
- **Documentation**: [terminal.info-tech.io](https://terminal.info-tech.io)
- **Source Code**: [github.com/info-tech-io/web-terminal](https://github.com/info-tech-io/web-terminal)
- **Live Demo**: [terminal.info-tech.io/demo](https://terminal.info-tech.io/demo)

---

## 🛠️ InfoTech CLI - Development Automation Tools

**Command-line tools for automating InfoTech.io development workflows and site management.**

### Features
- **Module Management**: Create, update, and deploy educational modules
- **Template Operations**: Generate sites from hugo-templates
- **Batch Processing**: Bulk operations on multiple repositories
- **Workflow Automation**: Trigger builds and deployments
- **Content Validation**: Check markdown syntax and link validity

### Available Commands

#### Module Operations
```bash
# Create new educational module
info-tech module create --name "python-basics" --type educational

# Deploy module to production
info-tech module deploy --name "linux-advanced" --env production

# Validate module content
info-tech module validate --path ./mod_python_basics
```

#### Template Operations
```bash
# Generate site from template
info-tech template build --config module.json --output ./dist

# List available templates
info-tech template list

# Create custom template
info-tech template create --name "my-template" --base educational
```

#### Batch Operations
```bash
# Update all modules
info-tech batch update --pattern "mod_*"

# Rebuild all sites
info-tech batch rebuild --filter "type:educational"
```

### Installation
```bash
# Install via npm
npm install -g @info-tech-io/cli

# Or download binary
curl -L https://cli.info-tech.io/install.sh | bash
```

### Links
- **Documentation**: [cli.info-tech.io](https://cli.info-tech.io)
- **Source Code**: [github.com/info-tech-io/info-tech-cli](https://github.com/info-tech-io/info-tech-cli)
- **Installation Guide**: [cli.info-tech.io/install](https://cli.info-tech.io/install)

---

## 🔗 Product Integration

All our products are designed to work together seamlessly:

1. **Hugo Templates Factory** generates sites for INFOTEKA courses
2. **Quiz Engine** provides interactive assessments within courses
3. **Web Terminal** offers hands-on practice environments
4. **InfoTech CLI** automates development and deployment workflows

### Unified Workflow
```mermaid
graph LR
    A[Content Creation] --> B[Hugo Templates]
    B --> C[Quiz Engine Integration]
    C --> D[Web Terminal Labs]
    D --> E[INFOTEKA Platform]
    E --> F[InfoTech CLI Deployment]
```

## Getting Started

### For Learners
1. **Visit INFOTEKA**: [infotecha.ru](https://infotecha.ru)
2. **Choose a Course**: Start with Linux Basics
3. **Practice with Web Terminal**: Hands-on exercises
4. **Test Your Knowledge**: Interactive quizzes

### For Educators
1. **Review Templates**: [hugo.info-tech.io](https://hugo.info-tech.io)
2. **Create Content**: Use our educational template
3. **Add Quizzes**: Integrate Quiz Engine
4. **Deploy**: Use InfoTech CLI

### For Developers
1. **Read Our Guide**: [Developer Onboarding](/open-source/onboarding/)
2. **Choose a Product**: Pick an area of interest
3. **Contribute**: Submit pull requests
4. **Collaborate**: Join our community

## Support

- **Community Forum**: [github.com/orgs/info-tech-io/discussions](https://github.com/orgs/info-tech-io/discussions)
- **Documentation**: Each product has comprehensive docs
- **Bug Reports**: File issues in relevant repositories
- **Feature Requests**: Use GitHub Discussions

---

*All InfoTech.io products are open source and available under the MIT license.*