// unity/ServerGameManager.cs
using Mirror;
using UnityEngine;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text;
using System;

public class ServerGameManager : NetworkBehaviour
{
    public static ServerGameManager Instance;
    private static readonly HttpClient httpClient = new HttpClient();

    [Header("Backend Settings")]
    public string backendUrl = "http://localhost:8000";

    void Awake()
    {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    public async void HandlePlayerAction(string playerId, string action)
    {
        var payloadObj = new {
            player_id = playerId,
            action = action,
            timestamp = DateTime.UtcNow.ToString("o"),
            meta = new { source = "mirror_server" }
        };

        string json = JsonUtility.ToJson(payloadObj);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        try
        {
            var resp = await httpClient.PostAsync($"{backendUrl}/v1/session/default/action", content);
            var respText = await resp.Content.ReadAsStringAsync();

            // Broadcast to clients
            RpcBroadcastDMResponse(respText);
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to call backend: {e}");
            RpcBroadcastDMResponse("{\"narration\":\"The DM is unreachable.\", \"npc_dialogue\":[], \"events\":{}, \"player_choices\":[\"Wait\"], \"dm_notes\":\"backend error\"}");
        }
    }

    [ClientRpc]
    void RpcBroadcastDMResponse(string dmResponseJson)
    {
        UIManager.Instance.DisplayDMResponse(dmResponseJson);
    }
}
