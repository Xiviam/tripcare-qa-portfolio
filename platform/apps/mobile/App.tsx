import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

const API_URL = "http://10.0.2.2:8000";

type Booking = {
  id: number;
  pnr: string;
  last_name: string;
  status: string;
  contact_email: string;
  contact_phone: string;
};

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export default function App() {
  const [email, setEmail] = useState("customer@example.com");
  const [password, setPassword] = useState("Customer123!");
  const [token, setToken] = useState("");
  const [pnr, setPnr] = useState("TC1001");
  const [lastName, setLastName] = useState("Ivanov");
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function run(job: () => Promise<void>) {
    setLoading(true);
    setMessage("");
    try {
      await job();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Offline or API error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>TripCare Mobile</Text>
        <Text style={styles.muted}>Expo-клиент для smoke-проверки пассажирских сценариев.</Text>

        <View style={styles.section}>
          <Text style={styles.heading}>Login</Text>
          <TextInput style={styles.input} value={email} onChangeText={setEmail} autoCapitalize="none" />
          <TextInput style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
          <Pressable
            accessibilityRole="button"
            style={styles.button}
            onPress={() =>
              run(async () => {
                const data = await request<{ access_token: string }>("/auth/login", undefined, {
                  method: "POST",
                  body: JSON.stringify({ email, password }),
                });
                setToken(data.access_token);
                setMessage("Login successful");
              })
            }
          >
            <Text style={styles.buttonText}>Sign in</Text>
          </Pressable>
        </View>

        <View style={styles.section}>
          <Text style={styles.heading}>Booking search</Text>
          <TextInput style={styles.input} value={pnr} onChangeText={setPnr} autoCapitalize="characters" />
          <TextInput style={styles.input} value={lastName} onChangeText={setLastName} />
          <Pressable
            accessibilityRole="button"
            style={styles.button}
            disabled={!token}
            onPress={() =>
              run(async () => {
                const data = await request<Booking[]>(
                  `/bookings/search?pnr=${encodeURIComponent(pnr)}&last_name=${encodeURIComponent(lastName)}`,
                  token,
                );
                setBookings(data);
              })
            }
          >
            <Text style={styles.buttonText}>Find booking</Text>
          </Pressable>
        </View>

        {loading && <ActivityIndicator />}
        {message ? <Text style={styles.message}>{message}</Text> : null}

        {bookings.map((booking) => (
          <View key={booking.id} style={styles.booking}>
            <Text style={styles.heading}>{booking.pnr} · {booking.status}</Text>
            <Text>{booking.last_name}</Text>
            <Text>{booking.contact_email}</Text>
            <Text>{booking.contact_phone}</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#F4F7F8" },
  content: { padding: 20, gap: 16 },
  title: { fontSize: 30, fontWeight: "800", color: "#172026" },
  muted: { color: "#63717A" },
  section: { gap: 10, padding: 16, backgroundColor: "#FFFFFF", borderRadius: 8 },
  heading: { fontSize: 18, fontWeight: "700", color: "#172026" },
  input: { minHeight: 44, borderWidth: 1, borderColor: "#BAC7CE", borderRadius: 6, paddingHorizontal: 10 },
  button: { minHeight: 44, borderRadius: 6, backgroundColor: "#107F89", alignItems: "center", justifyContent: "center" },
  buttonText: { color: "#FFFFFF", fontWeight: "700" },
  message: { color: "#B42318" },
  booking: { padding: 16, gap: 6, borderWidth: 1, borderColor: "#D5E0E4", borderRadius: 8, backgroundColor: "#FFFFFF" },
});
