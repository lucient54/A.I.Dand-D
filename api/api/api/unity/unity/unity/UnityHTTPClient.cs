// unity/UnityHTTPClient.cs
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using System;

public class UnityHTTPClient : MonoBehaviour
{
    public IEnumerator SubmitAction(string sessionId, string playerId, string action, Action<string> onComplete)
    {
        var payload = new
        {
            player_id = playerId,
            action = action,
            timestamp = DateTime.UtcNow.ToString("o")
        };
        string json = JsonUtility.ToJson(payload);
        using (var request = new UnityWebRequest($"http://localhost:8000/v1/session/{sessionId}/action", "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                onComplete?.Invoke(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError("HTTP Submit failed: " + request.error);
                onComplete?.Invoke(null);
            }
        }
    }
}
