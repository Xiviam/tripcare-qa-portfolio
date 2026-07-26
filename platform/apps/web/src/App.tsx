import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  BadgePlus,
  BookOpen,
  CheckCircle2,
  ClipboardList,
  Contact,
  LogOut,
  Plane,
  RefreshCcw,
  Search,
  Shield,
  Ticket,
} from "lucide-react";
import { api, login } from "./api";
import { isBugEnabled } from "./bugMode";
import type { Article, BookingDetails, BookingSummary, Ticket as SupportTicket, User } from "./types";
import { baggagePreviewPrice, formatMoney, normalizePnr, validateContactInput } from "./utils";

type View = "search" | "contacts" | "baggage" | "refunds" | "knowledge" | "support" | "admin";

const demo = {
  customer: ["customer@example.com", "Customer123!"],
  agent: ["agent@example.com", "Agent123!"],
  admin: ["admin@example.com", "Admin123!"],
} as const;

export function App() {
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [email, setEmail] = useState<string>(demo.customer[0]);
  const [password, setPassword] = useState<string>(demo.customer[1]);
  const [pnr, setPnr] = useState("TC1001");
  const [lastName, setLastName] = useState("Ivanov");
  const [bookings, setBookings] = useState<BookingSummary[]>([]);
  const [selected, setSelected] = useState<BookingDetails | null>(null);
  const [view, setView] = useState<View>("search");
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  const canOpenAdmin = user?.role === "admin" || isBugEnabled("BUG-015");

  async function run<T>(job: () => Promise<T>, success?: string): Promise<T | null> {
    setLoading(true);
    setError("");
    setNotice("");
    try {
      const result = await job();
      if (success) setNotice(success);
      return result;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Неизвестная ошибка");
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    const nextToken = await run(() => login(email, password), "Вход выполнен");
    if (!nextToken) return;
    setToken(nextToken);
    const nextUser = await run(() => api.me(nextToken));
    if (nextUser) setUser(nextUser);
  }

  async function searchBookings(event?: FormEvent) {
    event?.preventDefault();
    if (!token) return;
    const normalizedPnr = normalizePnr(pnr, isBugEnabled("BUG-011"));
    const result = await run(() => api.searchBookings(token, normalizedPnr, lastName));
    if (result) {
      setBookings(result);
      if (result.length === 1) await openBooking(result[0].id);
    }
  }

  async function openBooking(id: number) {
    const details = await run(() => api.booking(token, id));
    if (details) {
      setSelected(details);
      setView("search");
    }
  }

  async function loadKnowledge(query = "baggage") {
    const data = await run(() => api.articles(query));
    if (data) setArticles(data);
  }

  async function loadTickets() {
    const data = await run(() => api.tickets(token));
    if (data) setTickets(data);
  }

  async function loadUsers() {
    const data = await run(() => api.users(token));
    if (data) setUsers(data);
  }

  useEffect(() => {
    if (token) {
      void searchBookings();
      void loadKnowledge();
      void loadTickets();
    }
    // The initial workspace load is intentionally keyed only by auth token.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const statusText = useMemo(() => selected?.status.replace("_", " ") ?? "booking not selected", [selected]);

  if (!token || !user) {
    return (
      <main className="login-shell">
        <section className="login-panel" aria-labelledby="login-title">
          <img src="/route-map.svg" alt="" className="brand-map" />
          <div>
            <p className="eyebrow">TripCare QA stand</p>
            <h1 id="login-title">Self-service passenger desk</h1>
            <p className="muted">
              Учебное приложение для проверки бронирований, багажа, возвратов и обращений.
            </p>
          </div>
          <form onSubmit={onLogin} className="stack">
            <label>
              Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" />
            </label>
            <label>
              Пароль
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                autoComplete="current-password"
              />
            </label>
            <div className="quick-logins" aria-label="Тестовые роли">
              {Object.entries(demo).map(([role, values]) => (
                <button
                  type="button"
                  key={role}
                  onClick={() => {
                    setEmail(values[0]);
                    setPassword(values[1]);
                  }}
                >
                  {role}
                </button>
              ))}
            </div>
            <button className="primary" type="submit">
              <CheckCircle2 size={18} aria-hidden="true" />
              Войти
            </button>
          </form>
          <Feedback loading={loading} notice={notice} error={error} />
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <Plane size={26} aria-hidden="true" />
          <div>
            <strong>TripCare</strong>
            <span>{user.email} · {user.role}</span>
          </div>
        </div>
        <button className="icon-button" onClick={() => window.location.reload()} title="Выйти">
          <LogOut size={18} aria-hidden="true" />
        </button>
      </header>

      <section className="workspace">
        <aside className="sidebar" aria-label="Разделы">
          <NavButton active={view === "search"} onClick={() => setView("search")} icon={<Search size={18} />}>
            Поиск
          </NavButton>
          <NavButton active={view === "contacts"} onClick={() => setView("contacts")} icon={<Contact size={18} />}>
            Контакты
          </NavButton>
          <NavButton active={view === "baggage"} onClick={() => setView("baggage")} icon={<BadgePlus size={18} />}>
            Багаж
          </NavButton>
          <NavButton active={view === "refunds"} onClick={() => setView("refunds")} icon={<RefreshCcw size={18} />}>
            Возврат
          </NavButton>
          <NavButton active={view === "knowledge"} onClick={() => setView("knowledge")} icon={<BookOpen size={18} />}>
            База знаний
          </NavButton>
          <NavButton active={view === "support"} onClick={() => setView("support")} icon={<Ticket size={18} />}>
            Поддержка
          </NavButton>
          {canOpenAdmin && (
            <NavButton active={view === "admin"} onClick={() => setView("admin")} icon={<Shield size={18} />}>
              Admin
            </NavButton>
          )}
        </aside>

        <section className="content">
          <div className="status-strip">
            <div>
              <span className="muted">Выбранное бронирование</span>
              <strong>{selected ? selected.pnr : "нет"}</strong>
            </div>
            <div>
              <span className="muted">Статус</span>
              <strong>{statusText}</strong>
            </div>
            <div>
              <span className="muted">Часовой пояс</span>
              <strong>{selected?.timezone ?? "-"}</strong>
            </div>
          </div>

          <Feedback loading={loading} notice={notice} error={error} />

          {view === "search" && (
            <SearchPanel
              pnr={pnr}
              setPnr={setPnr}
              lastName={lastName}
              setLastName={setLastName}
              searchBookings={searchBookings}
              bookings={bookings}
              selected={selected}
              openBooking={openBooking}
            />
          )}
          {view === "contacts" && selected && (
            <ContactsPanel booking={selected} token={token} reload={() => openBooking(selected.id)} run={run} />
          )}
          {view === "baggage" && selected && (
            <BaggagePanel booking={selected} token={token} reload={() => openBooking(selected.id)} run={run} />
          )}
          {view === "refunds" && selected && (
            <RefundPanel booking={selected} token={token} reload={() => openBooking(selected.id)} run={run} />
          )}
          {view === "knowledge" && (
            <KnowledgePanel articles={articles} loadKnowledge={loadKnowledge} hideEmpty={isBugEnabled("BUG-013")} />
          )}
          {view === "support" && selected && (
            <SupportPanel
              booking={selected}
              token={token}
              tickets={tickets}
              reload={async () => {
                await loadTickets();
                await openBooking(selected.id);
              }}
              run={run}
            />
          )}
          {view === "admin" && (
            <AdminPanel loadUsers={loadUsers} users={users} canLoad={user.role === "admin"} />
          )}
        </section>
      </section>
    </main>
  );
}

function Feedback({ loading, notice, error }: { loading: boolean; notice: string; error: string }) {
  return (
    <div className="feedback" aria-live="polite">
      {loading && <span>Загрузка...</span>}
      {notice && <span className="success">{notice}</span>}
      {error && <span className="error">{error}</span>}
    </div>
  );
}

function NavButton({
  active,
  onClick,
  icon,
  children,
}: {
  active: boolean;
  onClick: () => void;
  icon: JSX.Element;
  children: string;
}) {
  return (
    <button className={active ? "nav active" : "nav"} onClick={onClick}>
      {icon}
      <span>{children}</span>
    </button>
  );
}

function SearchPanel(props: {
  pnr: string;
  setPnr: (value: string) => void;
  lastName: string;
  setLastName: (value: string) => void;
  searchBookings: (event?: FormEvent) => Promise<void>;
  bookings: BookingSummary[];
  selected: BookingDetails | null;
  openBooking: (id: number) => Promise<void>;
}) {
  return (
    <section className="panel">
      <h2>Поиск бронирования</h2>
      <form className="search-row" onSubmit={props.searchBookings}>
        <label>
          PNR
          <input value={props.pnr} onChange={(event) => props.setPnr(event.target.value)} />
        </label>
        <label>
          Фамилия
          <input value={props.lastName} onChange={(event) => props.setLastName(event.target.value)} />
        </label>
        <button className="primary" type="submit">
          <Search size={18} aria-hidden="true" />
          Найти
        </button>
      </form>

      {props.bookings.length === 0 ? (
        <p className="empty">Бронирования не найдены.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>PNR</th>
                <th>Фамилия</th>
                <th>Статус</th>
                <th>Email</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {props.bookings.map((booking) => (
                <tr key={booking.id}>
                  <td>{booking.pnr}</td>
                  <td>{booking.last_name}</td>
                  <td><span className="badge">{booking.status}</span></td>
                  <td>{booking.contact_email}</td>
                  <td>
                    <button onClick={() => props.openBooking(booking.id)}>Открыть</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {props.selected && (
        <div className="details-grid">
          <section>
            <h3>Пассажиры</h3>
            {props.selected.passengers.map((passenger) => (
              <p key={passenger.id}>{passenger.first_name} {passenger.last_name}, место {passenger.seat}</p>
            ))}
          </section>
          <section>
            <h3>Рейсы</h3>
            {props.selected.flights.map((flight) => (
              <p key={flight.id}>{flight.flight_no}: {flight.origin} - {flight.destination}, {flight.status}</p>
            ))}
          </section>
        </div>
      )}
    </section>
  );
}

function ContactsPanel({
  booking,
  token,
  reload,
  run,
}: {
  booking: BookingDetails;
  token: string;
  reload: () => Promise<void>;
  run: <T>(job: () => Promise<T>, success?: string) => Promise<T | null>;
}) {
  const [email, setEmail] = useState(booking.contact_email);
  const [phone, setPhone] = useState(booking.contact_phone);
  const errors = validateContactInput(email, phone);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (errors.length) return;
    await run(() => api.updateContacts(token, booking.id, email, phone), "Контакты обновлены");
    await reload();
  }

  return (
    <section className="panel">
      <h2>Контактные данные</h2>
      <form className="stack narrow" onSubmit={submit}>
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <label>Телефон<input value={phone} onChange={(event) => setPhone(event.target.value)} /></label>
        {errors.map((item) => <span className="error" key={item}>{item}</span>)}
        <button className="primary" disabled={errors.length > 0}>Сохранить</button>
      </form>
    </section>
  );
}

function BaggagePanel({
  booking,
  token,
  reload,
  run,
}: {
  booking: BookingDetails;
  token: string;
  reload: () => Promise<void>;
  run: <T>(job: () => Promise<T>, success?: string) => Promise<T | null>;
}) {
  const passenger = `${booking.passengers[0]?.first_name ?? "Passenger"} ${booking.last_name}`;
  const [pieces, setPieces] = useState(1);
  const [weight, setWeight] = useState(20);
  const preview = baggagePreviewPrice(pieces, weight, isBugEnabled("BUG-012"));

  async function submit(event: FormEvent) {
    event.preventDefault();
    await run(() => api.addBaggage(token, booking.id, passenger, pieces, weight), "Багаж добавлен");
    await reload();
  }

  return (
    <section className="panel">
      <h2>Багаж</h2>
      <form className="search-row" onSubmit={submit}>
        <label>Мест<input type="number" min={1} max={5} value={pieces} onChange={(event) => setPieces(Number(event.target.value))} /></label>
        <label>Вес, кг<input type="number" min={1} max={45} value={weight} onChange={(event) => setWeight(Number(event.target.value))} /></label>
        <button className="primary"><BadgePlus size={18} aria-hidden="true" />Добавить</button>
      </form>
      <p>Предварительная стоимость: <strong>{formatMoney(preview)}</strong></p>
      {booking.baggage.map((item) => (
        <p key={item.id}>{item.passenger_name}: {item.pieces} шт., {item.weight_kg} кг, {formatMoney(item.price_cents)}</p>
      ))}
    </section>
  );
}

function RefundPanel({
  booking,
  token,
  reload,
  run,
}: {
  booking: BookingDetails;
  token: string;
  reload: () => Promise<void>;
  run: <T>(job: () => Promise<T>, success?: string) => Promise<T | null>;
}) {
  const [reason, setReason] = useState("Passenger cannot travel after schedule change");

  async function submit(event: FormEvent) {
    event.preventDefault();
    await run(() => api.createRefund(token, booking.id, reason), "Запрос на возврат создан");
    await reload();
  }

  return (
    <section className="panel">
      <h2>Возврат</h2>
      <form className="stack narrow" onSubmit={submit}>
        <label>Причина<textarea value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        <button className="primary"><RefreshCcw size={18} aria-hidden="true" />Создать запрос</button>
      </form>
      {booking.refunds.map((refund) => (
        <p key={refund.id}>{refund.status}: {refund.reason}</p>
      ))}
    </section>
  );
}

function KnowledgePanel({
  articles,
  loadKnowledge,
  hideEmpty,
}: {
  articles: Article[];
  loadKnowledge: (query: string) => Promise<void>;
  hideEmpty: boolean;
}) {
  const [query, setQuery] = useState("baggage");
  return (
    <section className="panel">
      <h2>База знаний</h2>
      <form
        className="search-row"
        onSubmit={(event) => {
          event.preventDefault();
          void loadKnowledge(query);
        }}
      >
        <label>Запрос<input value={query} onChange={(event) => setQuery(event.target.value)} /></label>
        <button className="primary"><BookOpen size={18} aria-hidden="true" />Искать</button>
      </form>
      {articles.length === 0 && !hideEmpty && <p className="empty">Статьи не найдены.</p>}
      <div className="article-list">
        {articles.map((article) => (
          <article key={article.id}>
            <h3>{article.title}</h3>
            <p>{article.body}</p>
            <span>{article.tags}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

function SupportPanel({
  booking,
  token,
  tickets,
  reload,
  run,
}: {
  booking: BookingDetails;
  token: string;
  tickets: SupportTicket[];
  reload: () => Promise<void>;
  run: <T>(job: () => Promise<T>, success?: string) => Promise<T | null>;
}) {
  const [subject, setSubject] = useState("Baggage question");
  const [message, setMessage] = useState("Please check baggage options for this booking.");
  const [severity, setSeverity] = useState("medium");

  async function submit(event: FormEvent) {
    event.preventDefault();
    await run(
      () => api.createTicket(token, booking.id, subject, message, isBugEnabled("BUG-014") ? "low" : severity),
      "Обращение создано",
    );
    await reload();
  }

  return (
    <section className="panel">
      <h2>Поддержка</h2>
      <form className="stack narrow" onSubmit={submit}>
        <label>Тема<input value={subject} onChange={(event) => setSubject(event.target.value)} /></label>
        <label>Сообщение<textarea value={message} onChange={(event) => setMessage(event.target.value)} /></label>
        <label>Приоритет
          <select value={severity} onChange={(event) => setSeverity(event.target.value)}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>
        <button className="primary"><Ticket size={18} aria-hidden="true" />Создать</button>
      </form>
      {tickets.map((ticket) => (
        <p key={ticket.id}>{ticket.subject}: {ticket.status}, {ticket.severity}</p>
      ))}
    </section>
  );
}

function AdminPanel({ loadUsers, users, canLoad }: { loadUsers: () => Promise<void>; users: User[]; canLoad: boolean }) {
  return (
    <section className="panel">
      <h2>Пользователи</h2>
      <button className="primary" onClick={loadUsers} disabled={!canLoad}>
        <ClipboardList size={18} aria-hidden="true" />
        Загрузить список
      </button>
      {!canLoad && <p className="empty">Доступ только для admin.</p>}
      {users.map((item) => (
        <p key={item.id}>{item.email}: {item.role}</p>
      ))}
    </section>
  );
}
