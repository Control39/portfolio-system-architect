# Components Interaction Diagram

## Mermaid Diagram

```mermaid
graph TD
    subgraph "Career Development System"
        CDS[app.py] --> DB[(SQLite)]
        CDS --> CSRF[Flask-WTF CSRF]
    end
    
    subgraph "Portfolio Organizer"
        PO[app.py] --> RA[Reasoning API]
    end
    
    subgraph "IT Compass"
        ITC[tracker.py] --> Markers[Markers]
    end
    
    subgraph "Arch Compass"
        AC[logger.py] --> Metrics[metrics.py]
    end
    
    subgraph "Cloud Reason"
        CR[convert_to_utf8.py]
    end
    
    CSRF -.-> PO
    ITC --> CDS
    AC --> PO
    CR --> AC
    PO --> CR

    classDef secure fill:#90EE90
    class CDS,PO,ITC,AC,CSRF secure
```

## Description

This diagram shows interconnections:
- **Career Development** ← Skills from **IT Compass**
- **Portfolio Organizer** ← Analysis from **Reasoning API** + **Arch Compass** monitoring
- **Cloud Reason** ← UTF-8 conversion support
- **Security** CSRF protection across Flask apps

