import React from &#39;react&#39;;
import { View, Text, StyleSheet } from &#39;react-native&#39;;

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Career Development System</Text>
      <Text>Mobile tracker – пока в разработке</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: &#39;center&#39;, alignItems: &#39;center&#39; },
  title: { fontSize: 20, fontWeight: &#39;bold&#39; },
});
