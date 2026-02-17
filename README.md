# 🏦 API-Agnostic Market Simulator

A protocol-agnostic exchange simulator built in Python that supports multiple messaging protocols (FIX and SBE) without modifying the core business engine.

This project demonstrates clean architectural separation between:

- **Protocol Layer (FIX / SBE / Custom Binary)**
- **Canonical Model Layer**
- **Core Matching Engine**
- **Transport Layer**

---

## 🚀 Features

- ✅ FIX 4.4 support (Logon, NewOrderSingle, ExecutionReport)
- ✅ Custom SBE-style binary protocol
- ✅ Multi-instrument order books
- ✅ Price-time priority matching
- ✅ Partial fills
- ✅ Basic risk management
- ✅ Order validation
- ✅ Protocol plug-in architecture
- ✅ Fully canonical core engine

---

## 🏗 Architecture Overview


            ┌────────────────────┐
            │     TCP Server     │
            └──────────┬─────────┘
                       │
            ┌──────────▼─────────┐
            │   Session Handler  │
            └──────────┬─────────┘
                       │
            ┌──────────▼─────────┐
            │   Protocol Plugin  │
            │  (FIX / SBE)       │
            └──────────┬─────────┘
                       │
            ┌──────────▼─────────┐
            │  Canonical Models  │
            └──────────┬─────────┘
                       │
            ┌──────────▼─────────┐
            │   Market Engine    │
            │ (Matching + Risk)  │
            └────────────────────┘


---

# 🧠 Design Philosophy

### 1️⃣ Protocol-Agnostic Core

The core engine:

- Does NOT know FIX tags
- Does NOT know binary offsets
- Does NOT know transport framing
- Only processes `CanonicalOrder`
- Only returns `CanonicalExecution`

This ensures protocol changes never affect the business logic.

---

### 2️⃣ Plugin-Based Protocol Layer

Each protocol implements:

```python
create_session_logic()
decode(raw_bytes)
map_to_canonical()
encode_execution()
encode_logon_ack()


market-simulator/
│
├── canonical/
│   └── messages.py
│
├── core/
│   ├── market_engine.py
│   ├── orderbook.py
│   ├── risk_manager.py
│   └── validator.py
│
├── plugins/
│   ├── fix_plugin.py
│   ├── sbe_plugin.py
│   └── base.py
│
├── session/
│   └── session_handler.py
│
├── transport/
│   └── tcp_server.py
│
└── main.py


